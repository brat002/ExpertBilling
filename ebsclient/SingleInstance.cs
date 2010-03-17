using System;
using System.Runtime.InteropServices;

namespace Single
{
    public class SingleInstance
    {
        private static readonly Guid SingleInstanceGuid = new Guid("7B357615-112B-429F-9DAF-D42BAA571185");

        private const int ERROR_ALREADY_EXISTS = 183; //код ошибки, возвращаемый в случае уже существующего события

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr CreateEvent(IntPtr lpEventAttributes, bool bManualReset, bool bInitialState, string lpName);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool CloseHandle(IntPtr hObject);

        private static IntPtr handle;

        public static bool IsSingleInstance()
        {
            handle = CreateEvent(IntPtr.Zero, false, false, SingleInstanceGuid.ToString());
            var error = Marshal.GetLastWin32Error();
            //Если событие уже существует, возвращаем false
            if (error == ERROR_ALREADY_EXISTS)
                return false;
            return true;
        }

        public static void CloseHandle()
        {
            CloseHandle(handle);
        }
    }
}
