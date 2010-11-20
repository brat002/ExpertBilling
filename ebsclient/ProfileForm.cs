using System;
using System.Windows.Forms;
using Preferences;

namespace ebsmon
{
    public partial class ProfileForm : Form
    {
        private const string DefaultPassword = "            ";

        private WindowPreferences _windowPreferences = new WindowPreferences();

        public WindowPreferences _WindowPreferences
        {
            get { return _windowPreferences; }
            set { _windowPreferences = value; }
        }

        public ProfileForm()
        {
            InitializeComponent();
        }

        private void buttonOk_Click(object sender, EventArgs e)
        {
            if (checkBoxMainWindowOpacity.Checked)
            { _WindowPreferences._Opacity = true; }
            else
            { _WindowPreferences._Opacity = false; }
            _WindowPreferences._OpacityValue = trackBarMainWindowOpacity.Value;

            if( isTopmost.Checked )
            { _WindowPreferences._TopMost = true; }
            else 
            { _WindowPreferences._TopMost = false; }
            
            if( isAutoRun.Checked )
            { _WindowPreferences._AutoRun = true; }
            else
            { _WindowPreferences._AutoRun = false; }

            if( isSavePassword.Checked )
            { _WindowPreferences._SavePassword = true;}
            else
            { _WindowPreferences._SavePassword = false; }

            if( textBoxLogin.Text != String.Empty )
            { _WindowPreferences._Login = textBoxLogin.Text; }
            else
            { _WindowPreferences._Login = String.Empty; }

            if( textBoxServerName.Text != String.Empty )
            { _WindowPreferences._ServerName = textBoxServerName.Text; }
            else
            {
                // always will be keeped previous state of server name
                //_WindowPreferences._ServerName = String.Empty;
            }
            if( textBoxPassword.Text != String.Empty )
            {
                if (isSavePassword.Checked
                    && textBoxLogin.Text != String.Empty)
                {
                    if (textBoxPassword.Text != DefaultPassword)
                    {
                        _WindowPreferences.SetPassword(textBoxPassword.Text);
                    }
                }
                else
                {
                    _WindowPreferences._EncryptPassword = String.Empty;
                }
            }
            
            this.Close();
        }

        private int LeftPos(int mainLeftPos)
        {
            
            if (mainLeftPos + this.Width > Screen.PrimaryScreen.WorkingArea.Width)
                return Screen.PrimaryScreen.WorkingArea.Width - this.Width;
            if (mainLeftPos < Screen.PrimaryScreen.WorkingArea.X)
                return Screen.PrimaryScreen.WorkingArea.X;
            return mainLeftPos;
        }

        private int TopPos(int mainTopPos)
        {
            if (mainTopPos < Screen.PrimaryScreen.WorkingArea.Top)
                return Screen.PrimaryScreen.WorkingArea.Top;
            if (mainTopPos + this.Height > Screen.PrimaryScreen.WorkingArea.Height)
                return Screen.PrimaryScreen.WorkingArea.Height - this.Height;
            return mainTopPos;
        }

        private void ProfileForm_Load(object sender, EventArgs e)
        {
            // 20 - offset between windows, not a magic number!!          
            this.Left = LeftPos(_WindowPreferences._XPosLeft);
            this.Top = TopPos(_WindowPreferences._YPosUpper);

            if ( _WindowPreferences._Opacity )
            {
                checkBoxMainWindowOpacity.Checked = true;
                trackBarMainWindowOpacity.Value = Convert.ToInt32(this.Owner.Opacity * 100);
            }
            else
            {
                trackBarMainWindowOpacity.Enabled = false;
                trackBarMainWindowOpacity.Value = _WindowPreferences._OpacityValue;
            }
            
            if ( _WindowPreferences._TopMost)
            {
                isTopmost.Checked = true;
            }
            if ( _WindowPreferences._AutoRun)
            {
                isAutoRun.Checked = true;
            }
            if ( _WindowPreferences._SavePassword && _WindowPreferences._Login != String.Empty)
            {
                isSavePassword.Checked = true;
            }
            if ( _WindowPreferences._SavePassword && _WindowPreferences._EncryptPassword != String.Empty && _WindowPreferences._Login != String.Empty)
            {
                // for do not show decrypted password
                textBoxPassword.Text = DefaultPassword;
            }
            
            if ( _WindowPreferences._Login != String.Empty )
            { textBoxLogin.Text = _WindowPreferences._Login; }
            else
            { isSavePassword.Enabled = false; }

            if ( _WindowPreferences._ServerName != String.Empty )
            {
                textBoxServerName.Text = _WindowPreferences._ServerName;
            }
        }

        private void textBoxPassword_TextChanged(object sender, EventArgs e)
        {
            if (textBoxLogin.Text == String.Empty
                || textBoxPassword.Text == String.Empty)
                isSavePassword.Enabled = false;
            else
            { isSavePassword.Enabled = true; }
        }

        private void textBoxLogin_TextChanged(object sender, EventArgs e)
        {
            if (textBoxLogin.Text == String.Empty 
                || textBoxPassword.Text == String.Empty)
                isSavePassword.Enabled = false;
            else
            { isSavePassword.Enabled = true; }
        }

        private void checkBoxMainWindowOpacity_CheckedChanged(object sender, EventArgs e)
        {
            if (checkBoxMainWindowOpacity.Checked)
            {
                trackBarMainWindowOpacity.Enabled = true;
                _WindowPreferences._Opacity = true;
                _WindowPreferences._OpacityValue = trackBarMainWindowOpacity.Value;
            }
            else
            {
                trackBarMainWindowOpacity.Enabled = false;
                _WindowPreferences._Opacity = false;
                this.Owner.Opacity = 1;
            }
        }

        private void trackBarMainWindowOpacity_Scroll(object sender, EventArgs e)
        {
            _WindowPreferences._OpacityValue = trackBarMainWindowOpacity.Value;
            this.Owner.Opacity = Convert.ToDouble(trackBarMainWindowOpacity.Value) / 100;
        }
    }
}