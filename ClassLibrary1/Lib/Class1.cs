using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Reflection;

using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using System.Windows.Media.Imaging;

namespace Ribbon
{
    class App : IExternalApplication
    {
        // define a method that will create our tab and button
        static void AddRibbonPanel(UIControlledApplication application)
        {
            // Create a custom ribbon tab
            String tabName = "TBO_Plugin";
            application.CreateRibbonTab(tabName);

            // Add a new ribbon panel
            RibbonPanel ribbonPanel = application.CreateRibbonPanel(tabName, "Layout Generation & Optimisation");

            // Get dll assembly path
            string thisAssemblyPath = Assembly.GetExecutingAssembly().Location;

            // create push button for Boundary Selection
            PushButtonData b1Data = new PushButtonData("cmdBoundary","Zoning",thisAssemblyPath,"TBO_Plugin.Boundary");
            PushButton pb1 = ribbonPanel.AddItem(b1Data) as PushButton;
            pb1.ToolTip = "Select Floor for Layout Generation";
            BitmapImage pb1Image = new BitmapImage(new Uri(@"C:\Users\sharm\OneDrive - Singapore University of Technology and Design\Term 8\01.401 - Capstone 2\Capstone\ClassLibrary1\images\zoningicon.png"));
            pb1.LargeImage = pb1Image;

            // create push button for Selection of Parameters
            PushButtonData b3Data = new PushButtonData("cmdParameters", "Parameters", thisAssemblyPath, "TBO_Plugin.Parameters");
            PushButton pb3 = ribbonPanel.AddItem(b3Data) as PushButton;
            pb3.ToolTip = "Select Constraints to Generate Layout & Objectives to Optimise Layout";
            BitmapImage pb3Image = new BitmapImage(new Uri(@"C:\Users\sharm\OneDrive - Singapore University of Technology and Design\Term 8\01.401 - Capstone 2\Capstone\ClassLibrary1\images\paramicon.png"));
            pb3.LargeImage = pb3Image;

            // create push button for Layout Generation Results
            PushButtonData b4Data = new PushButtonData("cmdLayout", "Layout", thisAssemblyPath, "TBO_Plugin.LayoutGeneration");
            PushButton pb4 = ribbonPanel.AddItem(b4Data) as PushButton;
            pb4.ToolTip = "Generate Iterations of Floor Plan Layouts";
            BitmapImage pb4Image = new BitmapImage(new Uri(@"C:\Users\sharm\OneDrive - Singapore University of Technology and Design\Term 8\01.401 - Capstone 2\Capstone\ClassLibrary1\images\layouticon.png"));
            pb4.LargeImage = pb4Image;
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            // do nothing
            return Result.Succeeded;
        }

        public Result OnStartup(UIControlledApplication application)
        {
            // call our method that will load up our toolbar
            AddRibbonPanel(application);
            return Result.Succeeded;
        }
    }
}
