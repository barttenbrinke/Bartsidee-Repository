boxee.enableLog(true);
boxee.autoChoosePlayer=true;
boxee.renderBrowser=False;

var btn_y = 374;
var btn_x1 = 16;


if (boxee.getVersion() > 3.0)
{
	boxee.setCanPause(true);
	boxee.setCanSkip(false);
	boxee.setCanSetVolume(false);
}

setTimeout(function(){
	boxee.getActiveWidget().click(btn_x1,btn_y);
},1000);

boxee.onPause = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}

boxee.onPlay = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}
