using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Windows.Forms;
using System.Xml.Serialization;

namespace Preferences
{
    public class WindowPreferences
    {
        public static int XPosLeft;
        public static int YPosUpper;
        public static bool Opacity;
        public static int OpacityScale;
        public static bool TopMost;
        public static bool AutoRun;
        public static bool SavePassword;
        public static string Login;
        private string _password;
        public static string EncryptPassword;
        public static string ServerName;
        private bool _disconnected;
        //private bool _isPreferences;

        public int _XPosLeft
        {
            get { return XPosLeft; }
            set { XPosLeft = value; }
        }

        public int _YPosUpper
        {
            get { return YPosUpper; }
            set { YPosUpper = value; }
        }

        public int _OpacityValue
        {
            get { return OpacityScale; }
            set { OpacityScale = value; }
        }

        public bool _Opacity
        {
            get { return Opacity; }
            set { Opacity = value; }
        }

        public bool _TopMost
        {
            get { return TopMost; }
            set { TopMost = value; }
        }

        public bool _AutoRun
        {
            get { return AutoRun; }
            set { AutoRun = value; }
        }

        public bool _SavePassword
        {
            get { return SavePassword; }
            set { SavePassword = value; }
        }

        public bool _Disconnected
        {
            get { return _disconnected; }
            set { _disconnected = value; }
        }

        public bool _IsPreferences
        {
            get
            {
                if ((_SavePassword)
                    && (_Login != String.Empty)
                    && (this._ServerName != String.Empty))
                    return true;
                return false;
            }
        }

        public string _Login
        {
            get { return Login; }
            set { Login = value; }
        }

        public void SetEncryptPassword( string openText )
        {
            _EncryptPassword = Encrypt(openText);
        }

        public void SetDecryptPassword( string encodedText )
        {
            SetPassword(Decrypt(encodedText));
        }
      
        public string _EncryptPassword
        {
            get { return EncryptPassword; }
            set { EncryptPassword = value; }
        }

        public string GetPassword()
        {
            return _password;
        }
        public void SetPassword(string new_password)
        {
            _password = new_password;
        }
        //public string _Password
        //{
        //    get
        //    {
        //        if( _password != String.Empty )
        //            return _password;
                
        //        if(EncryptPassword != String.Empty)
        //            return Decrypt(EncryptPassword);
                
        //        return "";
        //    }
        //    set { _password = value; }
        //}

        public string _ServerName
        {
            get { return ServerName; }
            set { ServerName = value; }
        }

        public void SavePreferences( int location_x, int location_y)
        {
            _XPosLeft = location_x;
            _YPosUpper = location_y;

            SetEncryptPassword(GetPassword());

            XmlSerializer xmlSerializer = new XmlSerializer(typeof(WindowPreferences));
            TextWriter textWriter = new StreamWriter("settings.xml");
            xmlSerializer.Serialize(textWriter, this);

            textWriter.Close();
        }

        /// <summary>
        /// Encrypt a string.
        /// </summary>
        /// <param name="originalString">The original string.</param>
        /// <returns>The encrypted string.</returns>
        /// <exception cref="ArgumentNullException">This exception will be thrown when the original string is null or empty.</exception>
        public static string Encrypt(string originalString)
        {
            byte[] bytes = ASCIIEncoding.ASCII.GetBytes("ZeroCool");

            if (String.IsNullOrEmpty(originalString))
            {
                throw new ArgumentNullException("The string which needs to be encrypted can not be null.");
            }

            DESCryptoServiceProvider cryptoProvider = new DESCryptoServiceProvider();
            MemoryStream memoryStream = new MemoryStream();
            CryptoStream cryptoStream = new CryptoStream(memoryStream, cryptoProvider.CreateEncryptor(bytes, bytes), CryptoStreamMode.Write);

            StreamWriter writer = new StreamWriter(cryptoStream);
            writer.Write(originalString);
            writer.Flush();
            cryptoStream.FlushFinalBlock();
            writer.Flush();

            return Convert.ToBase64String(memoryStream.GetBuffer(), 0, (int)memoryStream.Length);
        }

        /// <summary>
        /// Decrypt a crypted string.
        /// </summary>
        /// <param name="cryptedString">The crypted string.</param>
        /// <returns>The decrypted string.</returns>
        /// <exception cref="ArgumentNullException">This exception will be thrown when the crypted string is null or empty.</exception>
        public static string Decrypt(string cryptedString)
        {
            byte[] bytes = ASCIIEncoding.ASCII.GetBytes("ZeroCool");

            if (String.IsNullOrEmpty(cryptedString))
            {
                throw new ArgumentNullException("The string which needs to be decrypted can not be null.");
            }

            DESCryptoServiceProvider cryptoProvider = new DESCryptoServiceProvider();
            MemoryStream memoryStream = new MemoryStream(Convert.FromBase64String(cryptedString));
            CryptoStream cryptoStream = new CryptoStream(memoryStream, cryptoProvider.CreateDecryptor(bytes, bytes), CryptoStreamMode.Read);
            StreamReader reader = new StreamReader(cryptoStream);

            return reader.ReadToEnd();
        }

    }
}