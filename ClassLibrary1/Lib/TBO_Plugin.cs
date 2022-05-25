using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.DB.Architecture;
namespace TBO_Plugin
{
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class LayoutGeneration : IExternalCommand
    {
        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            //Get application and document objects
            UIApplication uiapp = commandData.Application;
            Document doc = uiapp.ActiveUIDocument.Document;
            View active = doc.ActiveView;
            Transaction trans = new Transaction(doc);

            try
            {
                //Defining selection filters, selection functions, level id, creating level element
                Selection sel = uiapp.ActiveUIDocument.Selection;
                FloorPickFilter floorFilter = new FloorPickFilter();
                DoorPickFilter doorFilter = new DoorPickFilter();
                ElementId level_id = new ElementId(311);
                Level lv1 = doc.GetElement(level_id) as Level;


                //Picking a floor
                TaskDialog.Show("Define Boundary", "Please select a floor");
                Reference pickedfloor = sel.PickObject(ObjectType.Element, floorFilter, "Select a floor"); //Calling method to prompt for floor input

                //Picking ingress
                TaskDialog.Show("Define Ingress", "Please select a door");
                Reference pickedingress = sel.PickObject(ObjectType.Element, doorFilter, "Select an ingress"); //Calling method to prompt for door input

                //Getting floor and ingress as Element
                Element floor = doc.GetElement(pickedfloor);
                Element ingress = doc.GetElement(pickedingress);

                //Finding location of ingress as XYZ
                Location ingress_loc = ingress.Location;
                LocationPoint ingress_lp = ingress_loc as LocationPoint;
                XYZ ingress_pt = ingress_lp.Point;

                //Getting bounding box of floor
                BoundingBoxXYZ bb = floor.get_BoundingBox(active);

                //Finding min and max point of bounding box
                XYZ min_pt = bb.Min;
                XYZ max_pt = bb.Max;

                //Defining grid size
                float grid_size = 1800f / 304.8f;

                //Finding x and y differences between right top corner and bottom left corner of bounding box
                float min_y = (float)min_pt.Y;
                float min_x = (float)min_pt.X;
                float max_y = (float)max_pt.Y;
                float max_x = (float)max_pt.X;
                int y_ax = 0;
                int x_ax = 0;
                float y_bound = max_y - min_y;
                float x_bound = max_x - min_x;

                if (y_bound % grid_size != 0)
                {
                    y_ax = (int)((int)(y_bound / grid_size));
                }
                if (x_bound % grid_size != 0)
                {
                    x_ax = (int)((int)(x_bound / grid_size));
                }

                //Forming matrix, m_xyz as list of Revit XYZ, m_id as matrix indexes
                var m_xyz = new List<List<XYZ>>();
                var m_id = new List<List<string>>();
                for (int y = 0; y < y_ax; y++)
                {
                    var x_id = new List<string>();
                    var y_id = new List<XYZ>();
                    for (int x = 0; x < x_ax; x++)
                    {
                        XYZ newpt = new XYZ((min_x + x * grid_size), (min_y + y * grid_size), 0);
                        y_id.Add(newpt);
                        x_id.Add("0");
                    }
                    m_xyz.Add(y_id);
                    m_id.Add(x_id);
                }
                
                //Finding index of point in matrix closest to ingress
                int min_dist_xid = 0;
                int min_dist_yid = 0;
                var y_dist = new List<float>();
                for (int y = 0; y < y_ax; y++)
                {
                    var x_dist = new List<float>();
                    for (int x = 0; x < x_ax; x++)
                    {
                        float distance = (float)m_xyz[y][x].DistanceTo(ingress_pt); //Finding distance of point in matrix to ingress point
                        x_dist.Add(distance); //Adding values to a list
                    }
                    min_dist_xid = x_dist.IndexOf(x_dist.AsQueryable().Min()); //Finding minimum distance from row of points
                    y_dist.Add(x_dist.AsQueryable().Min()); //Adding minimum distance to a list
                }
                min_dist_yid = y_dist.IndexOf(y_dist.AsQueryable().Min()); //Adding index minimum

                var min_dist_id = new List<int> { min_dist_yid, min_dist_xid };
                string y_ind = min_dist_id[0].ToString();
                string x_ind = min_dist_id[0].ToString();

                //Running python script and storing output
                dynamic output = PythonTest(y_ax, x_ax);

                //Breaking string for tags and walls
                List<string> splitlist = new List<string>();
                try
                {
                    string[] split = output.Split(new string[] {Environment.NewLine}, StringSplitOptions.RemoveEmptyEntries);
                    foreach (string line in split)
                    {
                        splitlist.Add(line);
                        //TaskDialog.Show("Line", line);
                    }
                }
                catch (Exception ex) 
                {
                    message = ex.Message;
                    TaskDialog.Show("failed", message);
                    return Result.Failed;
                }
                
                //Converting python output string to list<list<list<int>>>
                dynamic rect_index = Str_To_Index(splitlist[0]);

                //Creating list of lines to reference for wall creation 
                dynamic wall_lines = MakeWallLines(rect_index, m_xyz, doc, level_id, trans);
                
                //Starting transaction
                trans.Start("Wall Creation");

                //Creating walls in Revit
                for (int i = 0; i < wall_lines.Count; i++)
                {
                    for (int w = 0; w < wall_lines[i].Count; w++)
                    {
                        Wall walls = Wall.Create(doc, wall_lines[i][w], level_id, false);
                    }
                }

                //Closing transaction
                trans.Commit();

                //Getting plan topology and set of circuit plans (enclosed spaces) for level 1
                PlanTopology lv1topo = doc.get_PlanTopology(lv1);
                PlanCircuitSet CircuitSet = lv1topo.Circuits;
                

                //Creating room tags for each enclosed space
                //Starting transaction
                trans.Start("Room Tags");

                //Generating Room Tags
                int counter = 1; //Counter to keep track of room number
                foreach (PlanCircuit circuit in CircuitSet)
                {
                    counter++;
                    if (circuit.IsRoomLocated == false)
                    {
                        try
                        {
                            //Creating room and room tag for Reception
                            if ((int)Math.Floor(circuit.Area) == 391)
                            {
                                try
                                {
                                    //Creating room
                                    Room room = doc.Create.NewRoom(null, circuit); //Instantiating location of new room
                                    room.Name = "Reception";
                                    room.Number = String.Format("{0}", counter);
                                    Location room_loc = room.Location; //Finding location of room
                                    LocationPoint room_lp = room_loc as LocationPoint;
                                    XYZ room_pt = room_lp.Point;
                                    LinkElementId room_id = new LinkElementId(room.Id);
                                    UV uv = new UV(room_pt.X, room_pt.Y);
                                    RoomTag room_tag = doc.Create.NewRoomTag(room_id, uv, active.Id); //Creating room tag for generated room
                                }
                                catch (Exception ex)
                                {
                                    message = ex.Message;
                                    TaskDialog.Show("Reception Tag", message);
                                    return Result.Failed;
                                }
                            }

                            //Creating room and room tag for Consultation Rooms
                            else if ((int)Math.Floor(circuit.Area) == 124)
                            {
                                try
                                {
                                    //Creating room
                                    Room room = doc.Create.NewRoom(null, circuit); //Instantiating location of new room
                                    room.Name = "Consultation";
                                    room.Number = String.Format("{0}", counter);
                                    Location room_loc = room.Location; //Finding location of room
                                    LocationPoint room_lp = room_loc as LocationPoint;
                                    XYZ room_pt = room_lp.Point;
                                    LinkElementId room_id = new LinkElementId(room.Id);
                                    UV uv = new UV(room_pt.X, room_pt.Y);
                                    RoomTag room_tag = doc.Create.NewRoomTag(room_id, uv, active.Id); //Creating room tag for generated room
                                }
                                catch (Exception ex)
                                {
                                    message = ex.Message;
                                    TaskDialog.Show("Consultation Room Tag", message);
                                    return Result.Failed;
                                }
                            }

                            //Creating room and room tag for Handicap Toilets
                            else if ((int)Math.Floor(circuit.Area) == 256)
                            {
                                try
                                {
                                    //Creating room
                                    Room room = doc.Create.NewRoom(null, circuit); //Instantiating location of new room
                                    room.Name = "Handicap Toilet";
                                    room.Number = String.Format("{0}", counter);
                                    Location room_loc = room.Location; //Finding location of room
                                    LocationPoint room_lp = room_loc as LocationPoint;
                                    XYZ room_pt = room_lp.Point;
                                    LinkElementId room_id = new LinkElementId(room.Id);
                                    UV uv = new UV(room_pt.X, room_pt.Y);
                                    RoomTag room_tag = doc.Create.NewRoomTag(room_id, uv, active.Id); //Creating room tag for generated room
                                }
                                catch (Exception ex)
                                {
                                    message = ex.Message;
                                    TaskDialog.Show("Handicap Toilet Tag", message);
                                    return Result.Failed;
                                }
                            }

                            //Creating room and room tag for Toilets
                            else if ((int)Math.Floor(circuit.Area) == 58)
                            {
                                try
                                {
                                    //Creating room
                                    Room room = doc.Create.NewRoom(null, circuit); //Instantiating location of new room
                                    room.Name = "Toilet";
                                    room.Number = String.Format("{0}", counter);
                                    Location room_loc = room.Location;
                                    LocationPoint room_lp = room_loc as LocationPoint; //Finding location of room
                                    XYZ room_pt = room_lp.Point;
                                    LinkElementId room_id = new LinkElementId(room.Id);
                                    UV uv = new UV(room_pt.X, room_pt.Y);
                                    RoomTag room_tag = doc.Create.NewRoomTag(room_id, uv, active.Id); //Creating room tag for generated room
                                }
                                catch (Exception ex)
                                {
                                    message = ex.Message;
                                    TaskDialog.Show("Toilet Tag", message);
                                    return Result.Failed;
                                }
                            }

                            //Creating room and room tag for Unoccupied space
                            else
                            {
                                try
                                {
                                    //Creating room
                                    Room room = doc.Create.NewRoom(null, circuit); //Instantiating location of new room
                                    room.Name = "Unmatched";
                                    room.Number = String.Format("{0}", counter);
                                    Location room_loc = room.Location;
                                    LocationPoint room_lp = room_loc as LocationPoint; //Finding location of room
                                    XYZ room_pt = room_lp.Point;
                                    LinkElementId room_id = new LinkElementId(room.Id);
                                    UV uv = new UV(room_pt.X, room_pt.Y);
                                    RoomTag room_tag = doc.Create.NewRoomTag(room_id, uv, active.Id); //Creating room tag for generated room
                                }
                                catch (Exception ex)
                                {
                                    message = ex.Message;
                                    TaskDialog.Show("Empty Space", message);
                                    return Result.Failed;
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            message = ex.Message;
                            TaskDialog.Show("Empty Space", message);
                            return Result.Failed;
                        }
                    }
                }

                //Closing transaction
                trans.Commit();

                //Returning value of result for Execute command
                return Result.Succeeded;
            }
            //If the user right-clicks or presses Esc, handle the exception
            catch (Autodesk.Revit.Exceptions.OperationCanceledException)
            {
                return Result.Cancelled;
            }
            catch (Exception ex)
            {
                message = ex.Message;
                return Result.Failed;
            }
        }


        //Creating filter to constrain picking of elements to floors
        public class FloorPickFilter : ISelectionFilter
        {
            public bool AllowElement(Element e)
            {
                return (e.Category.Name == "Floors"); //Defining element category name to allow for selection

            }
            public bool AllowReference(Reference refer, XYZ point)
            {
                return false;
            }
        }

        //Creating filter to constrain the picking of elements to doors
        public class DoorPickFilter : ISelectionFilter
        {
            public bool AllowElement(Element e)
            {
                return (e.Category.Name == "Doors"); //Defining element category name to allow for selection

            }
            public bool AllowReference(Reference refer, XYZ point)
            {
                return false;
            }
        }

        //Creating method to call for running external python script
        public dynamic PythonTest(int cols, int rows)
        {
            try
            {
                string fileName = @"C:\Users\jovin\AppData\Local\Programs\Python\Python38\python.exe"; //Change the file directory to python.exe on your computer
                string python = @"C:\TBO_Plugin\Capstone\ClassLibrary1\python\test2.py"; //Change the file directory to the python file which is in the zip folder downloaded

                // Create process info
                Process psi = new Process();
                psi.StartInfo = new ProcessStartInfo(fileName);
                psi.StartInfo.Arguments = string.Format("{0} {1} {2}", python, cols, rows);

                //Defining ProcessStartInfo settings
                psi.StartInfo.UseShellExecute = false;
                psi.StartInfo.RedirectStandardOutput = true;
                psi.Start();
                psi.WaitForExit();
                dynamic output = psi.StandardOutput.ReadToEnd();
                dynamic exit = psi.ExitCode;
                return output;
            }
            catch (Exception ex)
            {
                string output = ex.Message;
                return output;
            }
        }

        //Creating method to convert string output from Python into a nested list of int (matrix)
        public dynamic Str_To_Index(string input)
        {
            List<List<List<int>>> rect = new List<List<List<int>>>();
            string[] clust = input.Split('S'); //Splitting output from python into substrings
            foreach (string c in clust)
            {
                List<List<int>> r_list = new List<List<int>>();
                string[] indiv_r = c.Split('A'); //Splitting substrings into further substrings
                foreach (string sub_r in indiv_r)
                {
                    List<int> r_index = new List<int>();
                    string[] rect_index = sub_r.Split(','); //Splitting into further substrings
                    foreach (string digit in rect_index)
                    {
                        try
                        {
                            int dig = Convert.ToInt32(digit); //Convert string to int
                            r_index.Add(dig); //Add int to list 
                        }
                        catch (Exception ex)
                        {
                            string message = ex.Message + " tostring";
                            TaskDialog.Show("digit", digit.GetType().ToString());
                            return message;
                        }
                    }
                    r_list.Add(r_index); //Adding list of int (matrix index) to a list
                }
                rect.Add(r_list); //Adding all indexes to a list
            }
            return rect;
        }

        //Creating method to convert string output from Python into room tags
        public dynamic Str_To_Tag(string input)
        {
            List<string> tag_list = new List<string>();
            string[] tags = input.Split('S'); //Splitting string into substrings
            foreach (string tag in tags)
            {
                try
                {
                    tag_list.Add(tag); //Adding string to list of tags
                }
                catch (Exception ex)
                {
                    string message = ex.Message;
                    TaskDialog.Show("Failed2", message);
                    return message;
                }
            }
            return tag_list;
        }

        //Creating method to convert indexes to Revit line bounds
        public dynamic MakeWallLines(dynamic input, dynamic m_xyz, Document doc, ElementId level_id, Transaction trans)
        {
            dynamic line_list = new List<List<Line>>();
            int count = 0;
            for (int clust = 0; clust < (int)input.Count; clust++)
            {
                dynamic l_list = new List<Line>();
                count++;
                for (int rect = 0; rect < 4; rect++)
                {
                    try
                    {
                        if (rect < 3)
                        {
                            Line l = Line.CreateBound(m_xyz[input[clust][rect][0]][input[clust][rect][1]], m_xyz[input[clust][rect + 1][0]][input[clust][rect + 1][1]]); //Creating bounds from index corresponding to index of points in m_xyz
                            l_list.Add(l);
                        }
                        else
                        {
                            Line l = Line.CreateBound(m_xyz[input[clust][rect][0]][input[clust][rect][1]], m_xyz[input[clust][0][0]][input[clust][0][1]]); //Creating bounds from index corresponding to index of points in m_xyz
                            l_list.Add(l);;
                        }
                    }
                    catch (Exception ex)
                    {
                        string message = ex.Message;
                        TaskDialog.Show("Failed", message);
                        return Result.Failed;
                    }
                }
                line_list.Add(l_list);
            }
            return line_list;
        }
    }
}
