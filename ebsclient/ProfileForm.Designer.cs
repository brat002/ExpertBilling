namespace ebsmon
{
    partial class ProfileForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(ProfileForm));
            this.buttonOk = new System.Windows.Forms.Button();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.checkBoxMainWindowOpacity = new System.Windows.Forms.CheckBox();
            this.trackBarMainWindowOpacity = new System.Windows.Forms.TrackBar();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.textBoxServerName = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.textBoxPassword = new System.Windows.Forms.TextBox();
            this.textBoxLogin = new System.Windows.Forms.TextBox();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.isAutoRun = new System.Windows.Forms.CheckBox();
            this.isTopmost = new System.Windows.Forms.CheckBox();
            this.isSavePassword = new System.Windows.Forms.CheckBox();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarMainWindowOpacity)).BeginInit();
            this.groupBox2.SuspendLayout();
            this.groupBox3.SuspendLayout();
            this.SuspendLayout();
            // 
            // buttonOk
            // 
            this.buttonOk.Location = new System.Drawing.Point(206, 307);
            this.buttonOk.Name = "buttonOk";
            this.buttonOk.Size = new System.Drawing.Size(75, 23);
            this.buttonOk.TabIndex = 5;
            this.buttonOk.Text = "Ok";
            this.buttonOk.UseVisualStyleBackColor = true;
            this.buttonOk.Click += new System.EventHandler(this.buttonOk_Click);
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.checkBoxMainWindowOpacity);
            this.groupBox1.Controls.Add(this.trackBarMainWindowOpacity);
            this.groupBox1.Location = new System.Drawing.Point(12, 220);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(269, 81);
            this.groupBox1.TabIndex = 13;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Визуализация: ";
            // 
            // checkBoxMainWindowOpacity
            // 
            this.checkBoxMainWindowOpacity.AutoSize = true;
            this.checkBoxMainWindowOpacity.Location = new System.Drawing.Point(6, 18);
            this.checkBoxMainWindowOpacity.Name = "checkBoxMainWindowOpacity";
            this.checkBoxMainWindowOpacity.Size = new System.Drawing.Size(180, 17);
            this.checkBoxMainWindowOpacity.TabIndex = 14;
            this.checkBoxMainWindowOpacity.Text = "Прозрачность главного окна: ";
            this.checkBoxMainWindowOpacity.UseVisualStyleBackColor = true;
            this.checkBoxMainWindowOpacity.CheckedChanged += new System.EventHandler(this.checkBoxMainWindowOpacity_CheckedChanged);
            // 
            // trackBarMainWindowOpacity
            // 
            this.trackBarMainWindowOpacity.LargeChange = 10;
            this.trackBarMainWindowOpacity.Location = new System.Drawing.Point(6, 34);
            this.trackBarMainWindowOpacity.Maximum = 100;
            this.trackBarMainWindowOpacity.Name = "trackBarMainWindowOpacity";
            this.trackBarMainWindowOpacity.Size = new System.Drawing.Size(253, 45);
            this.trackBarMainWindowOpacity.SmallChange = 10;
            this.trackBarMainWindowOpacity.TabIndex = 13;
            this.trackBarMainWindowOpacity.TickFrequency = 10;
            this.trackBarMainWindowOpacity.Value = 90;
            this.trackBarMainWindowOpacity.Scroll += new System.EventHandler(this.trackBarMainWindowOpacity_Scroll);
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.textBoxServerName);
            this.groupBox2.Controls.Add(this.label3);
            this.groupBox2.Controls.Add(this.label2);
            this.groupBox2.Controls.Add(this.label1);
            this.groupBox2.Controls.Add(this.textBoxPassword);
            this.groupBox2.Controls.Add(this.textBoxLogin);
            this.groupBox2.Location = new System.Drawing.Point(12, 12);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(269, 107);
            this.groupBox2.TabIndex = 14;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "Параметры подключения: ";
            // 
            // textBoxServerName
            // 
            this.textBoxServerName.Location = new System.Drawing.Point(94, 17);
            this.textBoxServerName.Name = "textBoxServerName";
            this.textBoxServerName.Size = new System.Drawing.Size(170, 20);
            this.textBoxServerName.TabIndex = 13;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(8, 20);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(80, 13);
            this.label3.TabIndex = 12;
            this.label3.Text = "Имя сервера: ";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(37, 82);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(51, 13);
            this.label2.TabIndex = 11;
            this.label2.Text = "Пароль: ";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(2, 51);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(86, 13);
            this.label1.TabIndex = 10;
            this.label1.Text = "Пользователь: ";
            // 
            // textBoxPassword
            // 
            this.textBoxPassword.Location = new System.Drawing.Point(94, 79);
            this.textBoxPassword.Name = "textBoxPassword";
            this.textBoxPassword.PasswordChar = '*';
            this.textBoxPassword.Size = new System.Drawing.Size(170, 20);
            this.textBoxPassword.TabIndex = 9;
            this.textBoxPassword.TextChanged += new System.EventHandler(this.textBoxPassword_TextChanged);
            // 
            // textBoxLogin
            // 
            this.textBoxLogin.Location = new System.Drawing.Point(94, 48);
            this.textBoxLogin.Name = "textBoxLogin";
            this.textBoxLogin.Size = new System.Drawing.Size(170, 20);
            this.textBoxLogin.TabIndex = 8;
            this.textBoxLogin.TextChanged += new System.EventHandler(this.textBoxLogin_TextChanged);
            // 
            // groupBox3
            // 
            this.groupBox3.Controls.Add(this.isAutoRun);
            this.groupBox3.Controls.Add(this.isTopmost);
            this.groupBox3.Controls.Add(this.isSavePassword);
            this.groupBox3.Location = new System.Drawing.Point(12, 125);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(268, 89);
            this.groupBox3.TabIndex = 15;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "Параметры запуска: ";
            // 
            // isAutoRun
            // 
            this.isAutoRun.AutoSize = true;
            this.isAutoRun.Location = new System.Drawing.Point(5, 65);
            this.isAutoRun.Name = "isAutoRun";
            this.isAutoRun.Size = new System.Drawing.Size(185, 17);
            this.isAutoRun.TabIndex = 12;
            this.isAutoRun.Text = "Запускать при старте системы";
            this.isAutoRun.UseVisualStyleBackColor = true;
            // 
            // isTopmost
            // 
            this.isTopmost.AutoSize = true;
            this.isTopmost.Location = new System.Drawing.Point(6, 42);
            this.isTopmost.Name = "isTopmost";
            this.isTopmost.Size = new System.Drawing.Size(147, 17);
            this.isTopmost.TabIndex = 11;
            this.isTopmost.Text = "Поверх остальных окон";
            this.isTopmost.UseVisualStyleBackColor = true;
            // 
            // isSavePassword
            // 
            this.isSavePassword.AutoSize = true;
            this.isSavePassword.Location = new System.Drawing.Point(6, 19);
            this.isSavePassword.Name = "isSavePassword";
            this.isSavePassword.Size = new System.Drawing.Size(121, 17);
            this.isSavePassword.TabIndex = 10;
            this.isSavePassword.Text = "Запомнить пароль";
            this.isSavePassword.UseVisualStyleBackColor = true;
            // 
            // ProfileForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(293, 335);
            this.Controls.Add(this.groupBox3);
            this.Controls.Add(this.groupBox2);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.buttonOk);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedToolWindow;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "ProfileForm";
            this.Text = "Профиль пользователя";
            this.Load += new System.EventHandler(this.ProfileForm_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.trackBarMainWindowOpacity)).EndInit();
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Button buttonOk;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.CheckBox checkBoxMainWindowOpacity;
        private System.Windows.Forms.TrackBar trackBarMainWindowOpacity;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.TextBox textBoxServerName;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBoxPassword;
        private System.Windows.Forms.TextBox textBoxLogin;
        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.CheckBox isAutoRun;
        private System.Windows.Forms.CheckBox isTopmost;
        private System.Windows.Forms.CheckBox isSavePassword;
    }
}