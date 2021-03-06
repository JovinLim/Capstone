using System;
using Python.Runtime;

namespace Python.Test
{
    /// <summary>
    /// Supports CLR threading / reentrant unit tests.
    /// </summary>
    public class ThreadTest
    {
        private static PyObject module;

        private static string testmod =
            "import clr\n" +
            "from Python.Test import ThreadTest\n" +
            "\n" +
            "def echostring(value):\n" +
            "    return value\n" +
            "\n" +
            "def echostring2(value):\n" +
            "    return ThreadTest.CallEchoString(value)\n" +
            "\n";


        /// <summary>
        /// This method calls back into the CPython runtime - tests
        /// call this from Python to check that we don't hang on
        /// nested transitions from managed to Python code and back.
        /// </summary>
        public static string CallEchoString(string arg)
        {
            using (Py.GIL())
            {
                if (module == null)
                {
                    module = PyModule.FromString("tt", testmod);
                }
                PyObject func = module.GetAttr("echostring");
                var parg = new PyString(arg);
                PyObject temp = func.Invoke(parg);
                var result = (string)temp.AsManagedObject(typeof(string));
                func.Dispose();
                parg.Dispose();
                temp.Dispose();
                return result;
            }
        }

        public static string CallEchoString2(string arg)
        {
            using (Py.GIL())
            {
                if (module == null)
                {
                    module = PyModule.FromString("tt", testmod);
                }

                PyObject func = module.GetAttr("echostring2");
                var parg = new PyString(arg);
                PyObject temp = func.Invoke(parg);
                var result = (string)temp.AsManagedObject(typeof(string));
                func.Dispose();
                parg.Dispose();
                temp.Dispose();
                return result;
            }
        }
    }
}
