function addEvent(obj,type,fn){if( obj.attachEvent ){obj["e"+type+fn] = fn;obj[type+fn] = function(){obj["e"+type+fn]( window.event );}
obj.attachEvent( "on"+type, obj[type+fn] );} else
obj.addEventListener(type,fn,false);}
function removeEvent(obj,type,fn){if( obj.detachEvent ){obj.detachEvent( "on"+type, obj[type+fn] );obj[type+fn] = null;} else
obj.removeEventListener(type,fn,false);}
function $(){var elements=new Array();for(var i=0;i < arguments.length;i++){var element=arguments[i];if(typeof element == 'string')
element=document.getElementById(element);if(arguments.length==1) 
return element;elements.push(element);}
return elements;}
function econvert(s){return s.replace(/%7E/g,'~').replace(/%28/g,'(').replace(/%29/g,')').replace(/%20/g,' ')
.replace(/_dot_|_dot | dot_| dot |_\._|\(\.\)/gi, '.').replace(/_at_|_@_|~at~/gi, '@');}
function AEHit(){var sp=document.getElementsByTagName("span");for(i=0;i< sp.length;i++)if(sp[i].className=="aeh") 
sp[i].innerHTML=econvert(sp[i].innerHTML);}
addEvent(window, 'load', AEHit);function getCookieVal (offset){var endstr=document.cookie.indexOf (";", offset);if(endstr==-1)
endstr=document.cookie.length;return unescape(document.cookie.substring(offset,endstr));}
function FixCookieDate (date){var base=new Date(0);var skew=base.getTime();if(skew > 0)
date.setTime (date.getTime() - skew);}
function GetCookie (name){var arg=name + "=";var alen=arg.length;var clen=document.cookie.length;var i=0;while(i < clen){var j=i + alen;if(document.cookie.substring(i,j) == arg)
return getCookieVal (j);i=document.cookie.indexOf(" ", i) + 1;if(i==0) break;}
return null;}
function SetCookie (name,value,expires,path,domain,secure){document.cookie=name + "=" + escape (value) +
((expires) ? ";expires=" + expires.toGMTString() : "") +
((path) ? ";path=" + path : "") +
((domain) ? ";domain=" + domain : "") +
((secure) ? ";secure" : "");}
function DeleteCookie (name,path,domain) {if(GetCookie(name)){document.cookie=name + "=" +
((path) ? ";path=" + path : "") +
((domain) ? ";domain=" + domain : "") +
";expires=Thu, 01-Jan-70 00:00:01 GMT";}}
function show(id){$(id).style['display']='';if($(id).className.indexOf('hidden')>-1)
$(id).className = $(id).className.replace('hidden','');}
function hide(id){$(id).style['display']='none';}
function sack(file){this.AjaxFailedAlert = "Your browser does not support the enhanced functionality of this website, and therefore you will have an experience that differs from the intended one.\n";this.requestFile=file;this.method = "POST";this.URLString = "";this.encodeURIString=true;this.execute=false;this.onLoading=function(){};this.onLoaded=function(){};this.onInteractive=function(){};this.onCompletion=function(){};this.createAJAX=function(){try{this.xmlhttp=new ActiveXObject("Msxml2.XMLHTTP");} catch(e){try{this.xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");} catch(err){this.xmlhttp=null;}}if(!this.xmlhttp && typeof XMLHttpRequest != "undefined")
this.xmlhttp=new XMLHttpRequest();if(!this.xmlhttp){this.failed=true;}};this.setVar=function(name,value){if(this.URLString.length < 3){this.URLString=name + "=" + value;}else{this.URLString+="&" + name + "=" + value;}}
this.encVar=function(name,value){var varString=encodeURIComponent(name) + "=" + encodeURIComponent(value);return varString;}
this.encodeURLString=function(string){varArray=string.split('&');for(i=0;i < varArray.length;i++){urlVars=varArray[i].split('=');if(urlVars[0].indexOf('amp;')!=-1){urlVars[0] = urlVars[0].substring(4);}
varArray[i] = this.encVar(urlVars[0],urlVars[1]);}
return varArray.join('&');}
this.runResponse=function(){eval(this.response);}
this.runAJAX=function(urlstring){this.responseStatus=new Array(2);if(this.failed && this.AjaxFailedAlert){alert(this.AjaxFailedAlert);}else{if(urlstring){if(this.URLString.length){this.URLString=this.URLString + "&" + urlstring;}else{this.URLString=urlstring;}}if(this.encodeURIString){var timeval=new Date().getTime();this.URLString=this.encodeURLString(this.URLString);this.setVar("rndval", timeval);}if(this.element){this.elementObj=document.getElementById(this.element);}if(this.xmlhttp){var self=this;if(this.method=="GET"){var totalurlstring=this.requestFile + "?" + this.URLString;this.xmlhttp.open(this.method, totalurlstring, true);}else{this.xmlhttp.open(this.method, this.requestFile, true);}if(this.method=="POST"){try{this.xmlhttp.setRequestHeader('Content-Type','application/x-www-form-urlencoded')} catch(e){}}
this.xmlhttp.send(this.URLString);this.xmlhttp.onreadystatechange=function(){switch (self.xmlhttp.readyState){case 1:
self.onLoading();break;
case 2:
self.onLoaded();break;
case 3:
self.onInteractive();break;
case 4:
self.response=self.xmlhttp.responseText;self.responseXML=self.xmlhttp.responseXML;self.responseStatus[0] = self.xmlhttp.status;self.responseStatus[1] = self.xmlhttp.statusText;self.onCompletion();if(self.execute){self.runResponse();}if(self.elementObj){var elemNodeName=self.elementObj.nodeName;elemNodeName.toLowerCase();if(elemNodeName == "input" || elemNodeName == "select" || elemNodeName == "option" || elemNodeName == "textarea"){self.elementObj.value=self.response;}else{self.elementObj.innerHTML=self.response;}}
self.URLString = "";break;}};}}};this.createAJAX();}
