using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Win32;


namespace ebsmon
{
    class AutoRun
    {
        private RegistryKey autorunKey;

        public void AddKey(string programName, string executablePath)
        {
            this.autorunKey = Registry.LocalMachine.OpenSubKey(
                @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", true);
            try
            {
                autorunKey.SetValue("ebsmon", executablePath);
            }
            catch(System.NullReferenceException)
            {
                throw new System.NullReferenceException();
            }
            catch (Exception)
            {
                //throw;
            }
            
        }
        public void DeleteKey(string programName)
        {
            this.autorunKey = Registry.LocalMachine.OpenSubKey(
                @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", true);
            try
            {
                autorunKey.DeleteValue("ebsmon");
            }
            catch (NullReferenceException)
            {
                throw new NullReferenceException();
            }
            catch (Exception)
            {
                //throw;
            }
        }
    }
}
