using System;
using System.Collections.Generic;

namespace ServiceData
{
    static class ServiceConstants
    {
        public const string SERVER_UNAVABLE = "1007";
        public const string NOT_AUTHENTICATED = "1008";
        public const string BALANCE_REQUEST = "1009";
        public const string BALANCE_RESPONSE = "1010";
        public const string PREP_TRAFF_REQUEST = "1011";
        public const string PREP_TRAFF_RESPONSE = "1012";
        public const string PREP_TIME_REQUEST = "1013";
        public const string PREP_TIME_RESPONSE = "1014";
        public const string LIMIT_REST_REQUEST = "1015";
        public const string LIMIT_REST_RESPONSE = "1016";
        public const string NEWS_REQUEST = "1017";
        public const string NEWS_RESPONSE = "1018";
        public const string BALANCE_BLOCK_REQUEST = "1019";
        public const string BALANCE_BLOCK_RESPONSE = "1020";
        public const string LIMIT_BLOCK_REQUEST = "1021";
        public const string LIMIT_BLOCK_RESPONSE = "1022";

        public static string MessageByStatusCode(string statusCode)
        {
            switch (statusCode)
            {
                case ServiceConstants.SERVER_UNAVABLE:
                    return ebsmon.Properties.Resources.ConnectionFault;
                case ServiceConstants.NOT_AUTHENTICATED:
                    return ebsmon.Properties.Resources.AuthorizationError;
                default:
                    return String.Empty;
            }
        }
    }

    class ResponseData
    {
        private Dictionary<string, string> _data;

        public Dictionary<string, string> _Data
        {
            get { return _data; }
            set { _data = value; }
        }

        //public double BalanceToDouble()
        //{
        //    try
        //    {   
        //        return Convert.ToDouble(BalanceToString());
        //    }
        //    catch (Exception)
        //    {
        //        return float.NaN;
        //    }
            
        //}

        public string GetValue()
        {
            if ((_Data["status_code"] == ServiceConstants.SERVER_UNAVABLE) ||
                (_Data["status_code"] == ServiceConstants.NOT_AUTHENTICATED))
                return String.Empty;
            return _Data["value"];
        }

        public string ValueToString()
        {
            if (_Data["status_code"] == ServiceConstants.BALANCE_RESPONSE)
            {
                return _Data["value"].Replace('.', ',');
            }
            return string.Empty;
        }
    }

    

}
