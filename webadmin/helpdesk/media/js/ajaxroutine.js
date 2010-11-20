//Basic Ajax Routine- Author: Dynamic Drive (http://www.dynamicdrive.com)
//Last updated: Jan 15th, 06'

function createAjaxObj(){
var httprequest=false
if (window.XMLHttpRequest){ // if Mozilla, Safari etc
httprequest=new XMLHttpRequest()
if (httprequest.overrideMimeType)
httprequest.overrideMimeType('text/xml')
}
else if (window.ActiveXObject){ // if IE
try {
httprequest=new ActiveXObject("Msxml2.XMLHTTP");
} 
catch (e){
try{
httprequest=new ActiveXObject("Microsoft.XMLHTTP");
}
catch (e){}
}
}
return httprequest
}

var ajaxpack=new Object()
ajaxpack.basedomain="http://"+window.location.hostname
ajaxpack.ajaxobj=createAjaxObj()
ajaxpack.filetype="txt"
ajaxpack.addrandomnumber=0 //Set to 1 or 0. See documentation.

ajaxpack.getAjaxRequest=function(url, parameters, callbackfunc, filetype){
ajaxpack.ajaxobj=createAjaxObj() //recreate ajax object to defeat cache problem in IE
if (ajaxpack.addrandomnumber==1) //Further defeat caching problem in IE?
var parameters=parameters+"&ajaxcachebust="+new Date().getTime()
if (this.ajaxobj){
this.filetype=filetype
this.ajaxobj.onreadystatechange=callbackfunc
this.ajaxobj.open('GET', url+"?"+parameters, true)
this.ajaxobj.send(null)
}
}

ajaxpack.postAjaxRequest=function(url, parameters, callbackfunc, filetype){
ajaxpack.ajaxobj=createAjaxObj() //recreate ajax object to defeat cache problem in IE
if (this.ajaxobj){
this.filetype=filetype
this.ajaxobj.onreadystatechange = callbackfunc;
this.ajaxobj.open('POST', url, true);
this.ajaxobj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
this.ajaxobj.setRequestHeader("Content-length", parameters.length);
this.ajaxobj.setRequestHeader("Connection", "close");
this.ajaxobj.send(parameters);
}
}

//ACCESSIBLE VARIABLES (for use within your callback functions):
//1) ajaxpack.ajaxobj //points to the current ajax object
//2) ajaxpack.filetype //The expected file type of the external file ("txt" or "xml")
//3) ajaxpack.basedomain //The root domain executing this ajax script, taking into account the possible "www" prefix.
//4) ajaxpack.addrandomnumber //Set to 0 or 1. When set to 1, a random number will be added to the end of the query string of GET requests to bust file caching of the external file in IE. See docs for more info.

//ACCESSIBLE FUNCTIONS:
//1) ajaxpack.getAjaxRequest(url, parameters, callbackfunc, filetype)
//2) ajaxpack.postAjaxRequest(url, parameters, callbackfunc, filetype)

///////////END OF ROUTINE HERE////////////////////////


//////EXAMPLE USAGE ////////////////////////////////////////////
/* Comment begins here

//Define call back function to process returned data
function processGetPost(){
var myajax=ajaxpack.ajaxobj
var myfiletype=ajaxpack.filetype
if (myajax.readyState == 4){ //if request of file completed
if (myajax.status==200 || window.location.href.indexOf("http")==-1){ if request was successful or running script locally
if (myfiletype=="txt")
alert(myajax.responseText)
else
alert(myajax.responseXML)
}
}
}

/////1) GET Example- alert contents of any file (regular text or xml file):

ajaxpack.getAjaxRequest("example.php", "", processGetPost, "txt")
ajaxpack.getAjaxRequest("example.php", "name=George&age=27", processGetPost, "txt")
ajaxpack.getAjaxRequest("examplexml.php", "name=George&age=27", processGetPost, "xml")
ajaxpack.getAjaxRequest(ajaxpack.basedomain+"/mydir/mylist.txt", "", processGetPost, "txt")

/////2) Post Example- Post some data to a PHP script for processing, then alert posted data:

//Define function to construct the desired parameters and their values to post via Ajax
function getPostParameters(){
var namevalue=document.getElementById("namediv").innerHTML //get name value from a DIV
var agevalue=document.getElementById("myform").agefield.value //get age value from a form field
var poststr = "name=" + encodeURI(namevalue) + "&age=" + encodeURI(agevalue)
return poststr
}

var poststr=getPostParameters()

ajaxpack.postAjaxRequest("example.php", poststr, processGetPost, "txt")
ajaxpack.postAjaxRequest("examplexml.php", poststr, processGetPost, "xml")

Comment Ends here */