using System;
using System.IO;
using System.Net;
using System.Text;
//using System.Threading;

namespace EbsWebClient
{
    public class ConnectionTimeoutExeption:Exception
    {
        public string delayTimeoutMessage;
        public ConnectionTimeoutExeption(string msg):base("WebClient exeption")
        {
            delayTimeoutMessage = msg;
        }
    }
    
    class Client
    {
        private HttpWebRequest _httpWebRequest;
        private HttpWebResponse _httpWebResponse;
        private string _loginUrl;
        private string _cookieString;
        public const int MAX_CONNECTIONS_COUNT = 10;
        private static int current_connections_count;

        public static void ConnectionCountReset()
        {
            current_connections_count = 0;
        }
        
        /// <summary>
        /// Client constructor
        /// </summary>
        /// <param name="loginUrl">Connection string for obtaining cookie string</param>
        public Client( string loginUrl )
        {
            // initialize httpWebRequest
            _loginUrl = loginUrl;
        }

        /// <summary>
        /// Initialize httpWebResponse for check connection or getting cookie
        /// </summary>
        /// <returns>Result of request</returns>
        public bool ConnectionRequest()
        {
            try
            {
                _httpWebRequest = (HttpWebRequest)HttpWebRequest.Create(_loginUrl);
                _httpWebRequest.UserAgent =
                    "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6";
                _httpWebRequest.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
                _httpWebRequest.Headers.Add("Accept-Language", "ru,en-us;q=0.7,en;q=0.3");
                _httpWebResponse = (HttpWebResponse)_httpWebRequest.GetResponse();
                return true;
            }
            
            catch(UriFormatException)
            {
                // uri is empty or incorrect
                return false;
            }

            catch (Exception)
            {
                return false;
            } 
        }

        /// <summary>
        /// Check "Set-Cookie" header to contain some cookie for login"
        /// </summary>
        /// <returns>CookieString or EmptyString</returns>
        protected string GetCookieString()
        {
            string sCookie = String.IsNullOrEmpty(_httpWebResponse.Headers["Set-Cookie"])
                                 ? String.Empty
                                 : _httpWebResponse.Headers["Set-Cookie"];
            return sCookie;
        }

        /// <summary>
        /// Authenticate on server with given login and password by session id
        /// </summary>
        /// <param name="login">login to connect to server</param>
        /// <param name="password">password to connect to server</param>
        /// <returns>Cookie string with session id for authenticated user or EmptyString</returns>
        public string SetConnection(string login, string password)
        {
            string sCookie = String.Empty;

            if (ConnectionRequest())
                sCookie = GetCookieString();
            else
            {
                return String.Empty;
            }

            _httpWebRequest = (HttpWebRequest)HttpWebRequest.Create(_loginUrl);
            _httpWebRequest.Method = "POST";
            _httpWebRequest.UserAgent =
                "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6";
            _httpWebRequest.Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
            _httpWebRequest.Headers.Add("Accept-Language", "ru,en-us;q=0.7,en;q=0.3");
            _httpWebRequest.ContentType = "application/x-www-form-urlencoded";
            _httpWebRequest.Headers.Add(HttpRequestHeader.Cookie, sCookie);
            _httpWebRequest.AllowAutoRedirect = false;
            string sQueryString = "username=" + login + "&password=" + password + "&next=%2F";
            byte[] bytes = Encoding.UTF8.GetBytes(sQueryString);
            _httpWebRequest.ContentLength = bytes.Length;
            _httpWebRequest.GetRequestStream().Write(bytes, 0, bytes.Length);

            _httpWebResponse = (HttpWebResponse) _httpWebRequest.GetResponse();

            _cookieString = GetCookieString();

            return _cookieString;
        }

        /// <summary>
        /// From some "url" whith "session id" getting JSON-encrypted string
        /// </summary>
        /// <param name="url">ulr to recive string</param>
        /// <returns>parsed JSON-encoded response string</returns>
        public string GetJsonString(string url)
        {
            string rez = String.Empty;
            _httpWebRequest = (HttpWebRequest)HttpWebRequest.Create(url);
            current_connections_count++;
            FillHeadersToRequest();

            if (current_connections_count < MAX_CONNECTIONS_COUNT)
            {
                try
                {
                    _httpWebResponse = (HttpWebResponse)_httpWebRequest.GetResponse();
                }
                catch (Exception)
                {
                    throw new ConnectionTimeoutExeption(ebsmon.Properties.Resources.ConnectionFault);
                }
                
            }
            else
            {
                throw new ConnectionTimeoutExeption(ebsmon.Properties.Resources.ConnectionFault);
            }

            rez = GetParsedResponse();
            current_connections_count--;
            _httpWebResponse.Close();

            return rez;
        }

        /// <summary>
        /// Fill headers of httpRequest to perform Request
        /// </summary>
        protected void FillHeadersToRequest()
        {
            _httpWebRequest.ContentType = "text/plain";
            _httpWebRequest.Headers.Add(HttpRequestHeader.Cookie, _cookieString);
        }

        /// <summary>
        /// Represent string from html-formatted to C-formatted
        /// </summary>
        /// <returns>Parsed C-formatted represetn of html-string</returns>
        protected string GetParsedResponse()
        {
            string rez = String.Empty;

            StreamReader myStreamReader = new StreamReader(_httpWebResponse.GetResponseStream(),
                                                           Encoding.GetEncoding(1251));

            rez = myStreamReader.ReadToEnd();
            rez = rez.Replace("&quot;", "\"");
            rez = rez.Replace("\n", "");

            return rez;
        }
    }
}
