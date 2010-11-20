using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Threading;
using System.Windows.Forms;
using System.Xml.Serialization;
using CustomUIControls;
using System.Timers;
using System.Web.Script.Serialization;
using ebsmon.Properties;
using Preferences;
using VistaButtonTest;
using EbsWebClient;
using Events;
using ServiceData;
using Single;

namespace ebsmon
{
    /// <summary>
    /// Description for MainWindow form.
    /// </summary>
    public class MainWindow : Form
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private IContainer components;
        private NotifyIcon notifyIcon1;
        private ContextMenuStrip contextMenu;
        private ToolStripMenuItem menuItemProfile;
        private ToolStripMenuItem menuItemExit;
        private TextBox textBoxBalanceShow;
        private ToolStripSeparator toolStripSeparator1;
        private WindowPreferences winPrefs = new WindowPreferences();
        private System.Timers.Timer timerBalance;
        private System.Timers.Timer timerNews;
        private System.Timers.Timer timerConnect;
        private Button buttonShowNews;
        private VistaButton vistaButtonBalance;
        private VistaButton vistaButtonLimit;
        private VistaButton vistaButtonConnect;
        private Button buttonMinimize;
        private Button buttonClose;
        private Label label1;
        private Client client = new Client(String.Empty);
        private Thread connectionThread;

        /// <summary>
        /// Mouse track event id
        /// </summary>
        const int WM_NCHITTEST = 0x0084;

        /// <summary>
        /// additional event param
        /// </summary>
        const int HTCAPTION = 2;

        /// <summary>
        /// Override wnd proc for tracking 
        /// without capture
        /// </summary>
        /// <param name="m"></param>
        protected override void WndProc(ref Message m)
        {
            if (m.Msg == WM_NCHITTEST)
            {
                m.Result = (IntPtr)HTCAPTION;
                return;
            }
            base.WndProc(ref m);
        }

        
        /// <summary>
        /// Property for transferting data
        /// in prefs to form
        /// </summary>
        public WindowPreferences WinPrefs
        {
            get { return winPrefs; }
            set { winPrefs = value; }
        }

        /// <summary>
        /// Create and show main window components and initialize events
        /// </summary>
        public MainWindow()
        {
            //
            // Required for Windows Forms
            //
            InitializeComponent();
        }

        /// <summary>
        /// Destroy undeleted components
        /// </summary>
        protected override void Dispose(bool disposing)
        {
            try
            {
                winPrefs.SavePreferences(this.Location.X, this.Location.Y);
            }
            catch (IOException)
            {
                MessageBox.Show(Resources.SavePreferencesError, 
                    Resources.Title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            catch(Exception)
            {
                //MessageBox.Show(e.ToString());
            }
            
            if (disposing)
            {
                if (this.notifyIcon1 != null)
                    notifyIcon1.Visible = false;
                if (components != null)
                {
                    components.Dispose();
                }
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code
        /// <summary>
        /// Windows Form Designer generated code
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainWindow));
            this.textBoxBalanceShow = new System.Windows.Forms.TextBox();
            this.notifyIcon1 = new System.Windows.Forms.NotifyIcon(this.components);
            this.contextMenu = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.menuItemProfile = new System.Windows.Forms.ToolStripMenuItem();
            this.toolStripSeparator1 = new System.Windows.Forms.ToolStripSeparator();
            this.menuItemExit = new System.Windows.Forms.ToolStripMenuItem();
            this.buttonShowNews = new System.Windows.Forms.Button();
            this.buttonMinimize = new System.Windows.Forms.Button();
            this.buttonClose = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.vistaButtonBalance = new VistaButtonTest.VistaButton();
            this.vistaButtonLimit = new VistaButtonTest.VistaButton();
            this.vistaButtonConnect = new VistaButtonTest.VistaButton();
            this.contextMenu.SuspendLayout();
            this.SuspendLayout();
            // 
            // textBoxBalanceShow
            // 
            this.textBoxBalanceShow.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(209)))), ((int)(((byte)(230)))), ((int)(((byte)(253)))));
            this.textBoxBalanceShow.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.textBoxBalanceShow.Font = new System.Drawing.Font("Verdana", 14.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.textBoxBalanceShow.Location = new System.Drawing.Point(82, 36);
            this.textBoxBalanceShow.MaxLength = 10;
            this.textBoxBalanceShow.Name = "textBoxBalanceShow";
            this.textBoxBalanceShow.ReadOnly = true;
            this.textBoxBalanceShow.Size = new System.Drawing.Size(128, 24);
            this.textBoxBalanceShow.TabIndex = 3;
            this.textBoxBalanceShow.TabStop = false;
            this.textBoxBalanceShow.Text = "--------------";
            // 
            // notifyIcon1
            // 
            this.notifyIcon1.ContextMenuStrip = this.contextMenu;
            this.notifyIcon1.Icon = global::ebsmon.Properties.Resources.appicon;
            this.notifyIcon1.Text = "Ebs monitor";
            this.notifyIcon1.Visible = true;
            this.notifyIcon1.DoubleClick += new System.EventHandler(this.NotifyIcon1_DoubleClick);
            // 
            // contextMenu
            // 
            this.contextMenu.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.menuItemProfile,
            this.toolStripSeparator1,
            this.menuItemExit});
            this.contextMenu.Name = "contextMenuStrip1";
            this.contextMenu.Size = new System.Drawing.Size(205, 54);
            // 
            // menuItemProfile
            // 
            this.menuItemProfile.MergeIndex = 0;
            this.menuItemProfile.Name = "menuItemProfile";
            this.menuItemProfile.Size = new System.Drawing.Size(204, 22);
            this.menuItemProfile.Text = "Профиль пользователя";
            this.menuItemProfile.Click += new System.EventHandler(this.MenuItemProfile_Click);
            // 
            // toolStripSeparator1
            // 
            this.toolStripSeparator1.MergeIndex = 1;
            this.toolStripSeparator1.Name = "toolStripSeparator1";
            this.toolStripSeparator1.Size = new System.Drawing.Size(201, 6);
            // 
            // menuItemExit
            // 
            this.menuItemExit.MergeIndex = 2;
            this.menuItemExit.Name = "menuItemExit";
            this.menuItemExit.Size = new System.Drawing.Size(204, 22);
            this.menuItemExit.Text = "Выход";
            this.menuItemExit.Click += new System.EventHandler(this.MenuItemExit_Click);
            // 
            // buttonShowNews
            // 
            this.buttonShowNews.Location = new System.Drawing.Point(163, 64);
            this.buttonShowNews.Name = "buttonShowNews";
            this.buttonShowNews.Size = new System.Drawing.Size(42, 23);
            this.buttonShowNews.TabIndex = 4;
            this.buttonShowNews.TabStop = false;
            this.buttonShowNews.Text = "buttonShowNews";
            this.buttonShowNews.UseVisualStyleBackColor = true;
            this.buttonShowNews.Visible = false;
            this.buttonShowNews.Click += new System.EventHandler(this.buttonDisconnectMsg_Click);
            // 
            // buttonMinimize
            // 
            this.buttonMinimize.BackColor = System.Drawing.Color.Transparent;
            this.buttonMinimize.BackgroundImage = global::ebsmon.Properties.Resources.collapse;
            this.buttonMinimize.BackgroundImageLayout = System.Windows.Forms.ImageLayout.None;
            this.buttonMinimize.FlatAppearance.BorderColor = System.Drawing.Color.FromArgb(((int)(((byte)(17)))), ((int)(((byte)(37)))), ((int)(((byte)(61)))));
            this.buttonMinimize.FlatAppearance.BorderSize = 0;
            this.buttonMinimize.FlatAppearance.MouseDownBackColor = System.Drawing.Color.Transparent;
            this.buttonMinimize.FlatAppearance.MouseOverBackColor = System.Drawing.Color.Transparent;
            this.buttonMinimize.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.buttonMinimize.ForeColor = System.Drawing.Color.Transparent;
            this.buttonMinimize.ImageAlign = System.Drawing.ContentAlignment.BottomCenter;
            this.buttonMinimize.Location = new System.Drawing.Point(179, 11);
            this.buttonMinimize.Name = "buttonMinimize";
            this.buttonMinimize.Size = new System.Drawing.Size(11, 11);
            this.buttonMinimize.TabIndex = 9;
            this.buttonMinimize.UseVisualStyleBackColor = false;
            this.buttonMinimize.Click += new System.EventHandler(this.buttonMinimize_Click);
            // 
            // buttonClose
            // 
            this.buttonClose.BackColor = System.Drawing.Color.Transparent;
            this.buttonClose.BackgroundImage = ((System.Drawing.Image)(resources.GetObject("buttonClose.BackgroundImage")));
            this.buttonClose.BackgroundImageLayout = System.Windows.Forms.ImageLayout.None;
            this.buttonClose.FlatAppearance.BorderColor = System.Drawing.Color.FromArgb(((int)(((byte)(17)))), ((int)(((byte)(37)))), ((int)(((byte)(61)))));
            this.buttonClose.FlatAppearance.BorderSize = 0;
            this.buttonClose.FlatAppearance.MouseDownBackColor = System.Drawing.Color.Transparent;
            this.buttonClose.FlatAppearance.MouseOverBackColor = System.Drawing.Color.Transparent;
            this.buttonClose.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.buttonClose.ForeColor = System.Drawing.Color.Transparent;
            this.buttonClose.ImageAlign = System.Drawing.ContentAlignment.BottomCenter;
            this.buttonClose.Location = new System.Drawing.Point(194, 11);
            this.buttonClose.Name = "buttonClose";
            this.buttonClose.Size = new System.Drawing.Size(11, 11);
            this.buttonClose.TabIndex = 10;
            this.buttonClose.UseVisualStyleBackColor = false;
            this.buttonClose.Click += new System.EventHandler(this.buttonClose_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.BackColor = System.Drawing.Color.Transparent;
            this.label1.Font = new System.Drawing.Font("Verdana", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.label1.Location = new System.Drawing.Point(3, 39);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(80, 18);
            this.label1.TabIndex = 11;
            this.label1.Text = "Баланс:";
            // 
            // vistaButtonBalance
            // 
            this.vistaButtonBalance.BackColor = System.Drawing.Color.Transparent;
            this.vistaButtonBalance.BackgroundImageLayout = System.Windows.Forms.ImageLayout.None;
            this.vistaButtonBalance.BaseColor = System.Drawing.Color.Transparent;
            this.vistaButtonBalance.ButtonColor = System.Drawing.Color.Transparent;
            this.vistaButtonBalance.ButtonText = null;
            this.vistaButtonBalance.Cursor = System.Windows.Forms.Cursors.Default;
            this.vistaButtonBalance.ForeColor = System.Drawing.Color.Transparent;
            this.vistaButtonBalance.GlowColor = System.Drawing.Color.IndianRed;
            this.vistaButtonBalance.HighlightColor = System.Drawing.Color.Transparent;
            this.vistaButtonBalance.Image = global::ebsmon.Properties.Resources.balance_red;
            this.vistaButtonBalance.ImageAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.vistaButtonBalance.Location = new System.Drawing.Point(9, 64);
            this.vistaButtonBalance.Margin = new System.Windows.Forms.Padding(0);
            this.vistaButtonBalance.Name = "vistaButtonBalance";
            this.vistaButtonBalance.Size = new System.Drawing.Size(24, 24);
            this.vistaButtonBalance.TabIndex = 5;
            this.vistaButtonBalance.TabStop = false;
            // 
            // vistaButtonLimit
            // 
            this.vistaButtonLimit.BackColor = System.Drawing.Color.Transparent;
            this.vistaButtonLimit.BackgroundImageLayout = System.Windows.Forms.ImageLayout.None;
            this.vistaButtonLimit.BaseColor = System.Drawing.Color.Transparent;
            this.vistaButtonLimit.ButtonColor = System.Drawing.Color.Transparent;
            this.vistaButtonLimit.ButtonText = null;
            this.vistaButtonLimit.Cursor = System.Windows.Forms.Cursors.Default;
            this.vistaButtonLimit.ForeColor = System.Drawing.Color.Transparent;
            this.vistaButtonLimit.GlowColor = System.Drawing.Color.IndianRed;
            this.vistaButtonLimit.HighlightColor = System.Drawing.Color.Transparent;
            this.vistaButtonLimit.Image = global::ebsmon.Properties.Resources.limit_red;
            this.vistaButtonLimit.ImageAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.vistaButtonLimit.Location = new System.Drawing.Point(44, 64);
            this.vistaButtonLimit.Margin = new System.Windows.Forms.Padding(0);
            this.vistaButtonLimit.Name = "vistaButtonLimit";
            this.vistaButtonLimit.Size = new System.Drawing.Size(24, 24);
            this.vistaButtonLimit.TabIndex = 7;
            this.vistaButtonLimit.TabStop = false;
            // 
            // vistaButtonConnect
            // 
            this.vistaButtonConnect.BackColor = System.Drawing.SystemColors.Control;
            this.vistaButtonConnect.BackgroundImageLayout = System.Windows.Forms.ImageLayout.None;
            this.vistaButtonConnect.ButtonText = "Connect";
            this.vistaButtonConnect.Cursor = System.Windows.Forms.Cursors.Default;
            this.vistaButtonConnect.Font = new System.Drawing.Font("Comic Sans MS", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.vistaButtonConnect.Location = new System.Drawing.Point(118, 64);
            this.vistaButtonConnect.Margin = new System.Windows.Forms.Padding(0);
            this.vistaButtonConnect.Name = "vistaButtonConnect";
            this.vistaButtonConnect.Size = new System.Drawing.Size(42, 27);
            this.vistaButtonConnect.TabIndex = 8;
            this.vistaButtonConnect.Visible = false;
            this.vistaButtonConnect.Click += new System.EventHandler(this.ButtonConnect_Click);
            // 
            // MainWindow
            // 
            this.AutoScaleBaseSize = new System.Drawing.Size(9, 20);
            this.BackgroundImage = global::ebsmon.Properties.Resources.background;
            this.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Center;
            this.ClientSize = new System.Drawing.Size(215, 103);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.buttonClose);
            this.Controls.Add(this.buttonMinimize);
            this.Controls.Add(this.buttonShowNews);
            this.Controls.Add(this.textBoxBalanceShow);
            this.Controls.Add(this.vistaButtonBalance);
            this.Controls.Add(this.vistaButtonLimit);
            this.Controls.Add(this.vistaButtonConnect);
            this.DoubleBuffered = true;
            this.Font = new System.Drawing.Font("Verdana", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.ForeColor = System.Drawing.SystemColors.ActiveCaptionText;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.Name = "MainWindow";
            this.Text = "Ebs монитор";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.Resize += new System.EventHandler(this.Form1_Resize);
            this.contextMenu.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }
        #endregion

        /// <summary>
        /// Entry point for application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            if  (!SingleInstance.IsSingleInstance()) {
                MessageBox.Show(Properties.Resources.AppAlredyRunned, ebsmon.Properties.Resources.Title, MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                return;
            }
            try {
                Application.Run(new MainWindow());
            }
            catch (Exception)
            {
            }
            finally
            {
                SingleInstance.CloseHandle();
            }
        }

        private void CreateConnectionTimer()
        {
            timerConnect = new System.Timers.Timer();
            timerConnect.Interval = Convert.ToDouble(ebsmon.Properties.Resources.ConnectionTimerDelay);
            timerConnect.Elapsed += new ElapsedEventHandler(this.TimerConnectionElapsed);
            timerConnect.Enabled = true;
        }

        /// <summary>
        /// Concat the service data string
        /// </summary>
        /// <returns>Url on which is login procedure</returns>
        private string LoginUrl()
        {
            return ebsmon.Properties.Resources.ProtocolPrefix + winPrefs._ServerName +
                   ebsmon.Properties.Resources.ConnectionUrl;
        }

        private void ButtonConnect_Click(object sender, System.EventArgs e)
        {
            // Create new client to connect with a webserver
            client = new Client(LoginUrl());
            // Check connection with server)
            if (!client.ConnectionRequest())
            {
                if (!winPrefs._Disconnected)
                {
                    winPrefs._Disconnected = true;
                    ButtonClick(false); 
                }
                return;
            }

            // Set connection to web server and the sesion cookie
            // for use it in data exchange
            connectionThread = new Thread(SetConnection);
            connectionThread.Start();
            //string res = client.SetConnection(winPrefs._Login, winPrefs.GetPassword());
            //if ( string.IsNullOrEmpty(res) )
            //{
            //    if (winPrefs._Disconnected == false)
            //    {
            //        winPrefs._Disconnected = true;
            //    }

            //    if (client.ConnectionRequest())
            //    {
            //        MessageBox.Show(ebsmon.Properties.Resources.AuthorizationError, ebsmon.Properties.Resources.Title,
            //                        MessageBoxButtons.OK, MessageBoxIcon.Warning);
            //        CloseConnection(this, null);
            //        if (timerConnect != null)
            //            timerConnect.Close();
            //    }

            //    return;
            //}

            //timerConnect.Enabled = false;
            //// 
            //// timerBalance
            //// 
            //timerBalance = new System.Timers.Timer();
            //timerBalance.Interval = Convert.ToDouble(ebsmon.Properties.Resources.BalanceTimerDelay);
            //timerBalance.Elapsed += new ElapsedEventHandler(this.TimerBalanceElapsed);
            //timerBalance.Enabled = true;
            ////
            //// timerNews
            ////
            //timerNews = new System.Timers.Timer();
            //timerNews.Interval = Convert.ToDouble(ebsmon.Properties.Resources.NewsTimerDelay);
            //timerNews.Elapsed += new ElapsedEventHandler(this.TimerNewsElapsed);
            //timerNews.Enabled = true;
        }

        private void SetConnection()
        {
            string res = client.SetConnection(winPrefs._Login, winPrefs.GetPassword());
            if (string.IsNullOrEmpty(res))
            {
                if (winPrefs._Disconnected == false)
                {
                    winPrefs._Disconnected = true;
                }

                if (client.ConnectionRequest())
                {
                    MessageBox.Show(ebsmon.Properties.Resources.AuthorizationError, ebsmon.Properties.Resources.Title,
                                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    CloseConnection(this, null);
                    if (timerConnect != null)
                        timerConnect.Close();
                }

                return;
            }

            timerConnect.Enabled = false;
            // 
            // timerBalance
            // 
            timerBalance = new System.Timers.Timer();
            timerBalance.Interval = Convert.ToDouble(ebsmon.Properties.Resources.BalanceTimerDelay);
            timerBalance.Elapsed += new ElapsedEventHandler(this.TimerBalanceElapsed);
            timerBalance.Enabled = true;
            //
            // timerNews
            //
            timerNews = new System.Timers.Timer();
            timerNews.Interval = Convert.ToDouble(ebsmon.Properties.Resources.NewsTimerDelay);
            timerNews.Elapsed += new ElapsedEventHandler(this.TimerNewsElapsed);
            timerNews.Enabled = true;
        }
        
        /// <summary>
        /// Event handler for content click event in 
        /// notify messages
        /// </summary>
        /// <param name="obj"></param>
        /// <param name="newsMessageEventArgs">message to show</param>
        void ContentClick(object obj, NewsMessageEventArgs newsMessageEventArgs)
        {
            MessageBox.Show(newsMessageEventArgs.Message, ebsmon.Properties.Resources.NewsTitle);
        }
        
        private void LoadPreferences(FileStream fs)
        {
            XmlSerializer xmlSerializer = new XmlSerializer(typeof(WindowPreferences));
            winPrefs = (WindowPreferences)xmlSerializer.Deserialize(fs);
            winPrefs.SetDecryptPassword(winPrefs._EncryptPassword);
            winPrefs._Disconnected = false;
        }
        
        private void Form1_Load(object sender, EventArgs e)
        {
            try
            {
                FileStream fs = new FileStream("settings.xml", FileMode.Open);

                LoadPreferences(fs);

                this.Left = winPrefs._XPosLeft > 0 ? winPrefs._XPosLeft : 100;
                this.Top = winPrefs._YPosUpper > 0 ? winPrefs._YPosUpper : 100;
                
                if (winPrefs._Opacity)
                { this.Opacity = Convert.ToDouble(winPrefs._OpacityValue) / 100; }
                this.TopMost = winPrefs._TopMost;

                fs.Close();
            }
            catch (FileNotFoundException)
            {
                MessageBox.Show(ebsmon.Properties.Resources.RequiredSettingsError, ebsmon.Properties.Resources.Title);
                winPrefs._Disconnected = true;
            }

            CreateConnectionTimer();
            ButtonConnect_Click(this, null);
        }

        void Form1_Resize(object sender, EventArgs e)
        {
            if (this.WindowState == FormWindowState.Minimized)
            {
                this.ShowInTaskbar = false;
            }
        }

        private void NotifyIcon1_DoubleClick(object sender, EventArgs e)
        {
            // Show form when the user double clicks on the notify icon.

            // Set the WindowState to normal if the form is minimized.
            if (this.WindowState == FormWindowState.Minimized)
            {
                this.WindowState = FormWindowState.Normal;
                this.ShowInTaskbar = true;
                this.Show();
            }
            else
            {
                this.WindowState = FormWindowState.Minimized;
                this.ShowInTaskbar = false;
                this.Hide();
            }

            // Activate the form.
            this.Activate();
        }

        private void CloseConnection(object sender, EventArgs e)
        {
            // kill timers for current preferenses
            if (timerBalance != null)
            {
                timerBalance.Close();
            }
            if (timerNews != null)
            {
                timerNews.Close();
            }
        }

        private void MenuItemProfile_Click(object sender, EventArgs e)
        {
            // create window with preferences
            ProfileForm changeUserForm = new ProfileForm();
            // remember current pos of main window
            // to correct set position of pref window
            //MessageBox.Show("X = " + Screen.PrimaryScreen.WorkingArea.Width + "\nY = " + Screen.PrimaryScreen.WorkingArea.Height);
            winPrefs._XPosLeft = this.Location.X > 0 ? this.Location.X : winPrefs._XPosLeft;
            winPrefs._YPosUpper = this.Location.Y > 0 ? this.Location.Y : winPrefs._YPosUpper;
            // copy the winPrefs to a preferences window
            changeUserForm._WindowPreferences = winPrefs;
            // set property of new window
            // do not showing it in the taskbar
            changeUserForm.ShowInTaskbar = false;
            // show preferences window
            changeUserForm.ShowDialog(this);
            // save the result of changed user preferences
            winPrefs = changeUserForm._WindowPreferences;

            // recreate client with new preferences
            client = new Client(winPrefs._ServerName);

            if(winPrefs._IsPreferences)
            {
                SetInitialFormData();
                winPrefs._Disconnected = false;
                CloseConnection(this, null);
                if (timerConnect != null)
                    timerConnect.Close();
                CreateConnectionTimer();
                ButtonConnect_Click(this, null);
            }
            
        }

        private void MenuItemExit_Click(object sender, EventArgs e)
        {
            // Close the form, which closes the application.
            this.Close();
        }

        /// <summary>
        /// Concat the service data url string
        /// </summary>
        /// <returns>url on which is data exchange</returns>
        private string ServiceDataUrl()
        {
            return Resources.ProtocolPrefix + winPrefs._ServerName + Resources.ServiceDataUrl;
        }

        private string GetDataByRequestCode( string statusCode)
        {
            ResponseData response = new ResponseData();
            JavaScriptSerializer javaScriptSerializer = new JavaScriptSerializer();

            response._Data = (javaScriptSerializer.Deserialize<Dictionary<string, string>>(client.GetJsonString(ServiceDataUrl() + "?id=" + statusCode)));

            return response.GetValue();
        }

        private void TimerBalanceElapsed(object sender, EventArgs e)
        {
            try
            {
                string balance = GetDataByRequestCode(ServiceConstants.BALANCE_REQUEST);
                SetText(balance);

                string balanceBlock = GetDataByRequestCode(ServiceConstants.BALANCE_BLOCK_REQUEST);
                SetVistaButtonColor(Convert.ToBoolean(balanceBlock), true, vistaButtonBalance);

                string limitBlock = GetDataByRequestCode(ServiceConstants.LIMIT_BLOCK_REQUEST);
                SetVistaButtonColor(Convert.ToBoolean(limitBlock), false, vistaButtonLimit);
            }
            catch (ConnectionTimeoutExeption)
            {
                CloseConnection(this, null);
                Client.ConnectionCountReset();
                SetInitialFormData();
                timerConnect.Enabled = true;
                winPrefs._Disconnected = true;
                ButtonClick( false );
            }
        }

        /// <summary>
        /// Set color for VistaButtons
        /// </summary>
        /// <param name="isBlocked">blocked - red; else - ok</param>
        /// <param name="type">balance or limit </param>
        /// <param name="vistaButton">Balance or Limit</param>
        private void SetVistaButtonColor(bool isBlocked, bool type, VistaButton vistaButton)
        {
            if (isBlocked)
            {
                vistaButton.Image = type ? ebsmon.Properties.Resources.balance_red
                    : Properties.Resources.limit_red;
                vistaButton.GlowColor = System.Drawing.Color.IndianRed;
            }
            else
            {
                vistaButton.Image = type ? ebsmon.Properties.Resources.balance_ok
                    : Properties.Resources.limit_ok;
                vistaButton.GlowColor = System.Drawing.Color.PowderBlue;
            }
        }

        private void TimerNewsElapsed(object sender, EventArgs e)
        {
            ButtonClick( true );
        }

        private void TimerConnectionElapsed(object  sender, EventArgs e)
        {
            if (connectionThread != null && connectionThread.IsAlive)
                connectionThread.Abort();
            ButtonConnect_Click(this, null);
        }

        delegate void ButtonClickCallback(bool isNews);

        public void ButtonClick(bool isNews)
        {
            if (buttonShowNews.InvokeRequired)
            {
                buttonShowNews.Invoke(new ButtonClickCallback(ButtonClick), isNews);
            }
            else
            {
                if (isNews)
                {
                    buttonShowNews_Click(this, null);
                }
                else
                {
                    buttonDisconnectMsg_Click(this, null);
                }
            }
        }

        delegate void SetTextCallback(string text);
        
        public void SetText(string text)
        {
            if (textBoxBalanceShow.InvokeRequired)
            {
                textBoxBalanceShow.Invoke(new SetTextCallback(SetText), text);
            }
            else
            {
                textBoxBalanceShow.Text = text;
            }
        }

        private delegate void SetButtonStateCallback(bool state);

        public void EnableButton(bool state)
        {
            if (vistaButtonConnect.InvokeRequired)
            {
                vistaButtonConnect.Invoke(new SetButtonStateCallback(EnableButton), state);
            }
            else
            {
                vistaButtonConnect.Enabled = state;
            }
        }

        private void buttonShowNews_Click(object sender, EventArgs e)
        {
            try
            {
                string news = GetDataByRequestCode(ServiceConstants.NEWS_REQUEST);
                if (news != string.Empty)
                {
                    TaskbarNotifier taskBarNotifier = new TaskbarNotifier();
                    taskBarNotifier.ContentClick += new NewsMessageEventHandler(ContentClick);
                    taskBarNotifier.ShowNotifyMessage("", news);
                }
            }
            catch (ConnectionTimeoutExeption)
            {
            }
           
        }

        private void buttonDisconnectMsg_Click(object sender, EventArgs e)
        {
            TaskbarNotifier taskBarNotifier = new TaskbarNotifier();
            taskBarNotifier.ContentClick += new NewsMessageEventHandler(ContentClick);
            taskBarNotifier.ShowNotifyMessage("", ebsmon.Properties.Resources.ConnectionFault);
            SetInitialFormData();
        }

        private void SetInitialFormData()
        {
            SetText(ebsmon.Properties.Resources.DefaultBalanceString);
            vistaButtonBalance.Image = ebsmon.Properties.Resources.balance_red;
            vistaButtonLimit.Image = ebsmon.Properties.Resources.limit_red;
        }

        private void buttonMinimize_Click(object sender, EventArgs e)
        {
            NotifyIcon1_DoubleClick(this, null);
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            // Close the form, which closes the application.
            this.Close();
        }

    }
}