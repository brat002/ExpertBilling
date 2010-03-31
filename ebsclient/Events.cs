using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Events
{
    public class NewsMessageEventArgs: EventArgs
    {
        private string _message;

        public NewsMessageEventArgs(string _newsMessage)
        {
            this._message = _newsMessage;
        }
        public string Message
        {
            get { return _message; }
        }
    }

    public delegate void NewsMessageEventHandler(object sender, NewsMessageEventArgs e);


}
