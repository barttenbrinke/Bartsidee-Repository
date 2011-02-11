boxee.enableLog(true);
boxee.autoChoosePlayer=true;
boxee.renderBrowser=False;

var btn_y = 374;

var btn_x1 = 16;
var btn_x2 = 722;
var btn_x3 = 560;

var hasActive=false;
var Rescale=false;
var Subtitle=false;

if (boxee.getVersion() > 3.0)
{
	boxee.setCanPause(true);
	boxee.setCanSkip(false);
	boxee.setCanSetVolume(false);
}

function startPlay()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
	setTimeout(function() {if(Subtitle)
		{
			boxee.getActiveWidget().click(btn_x2,btn_y);
		}
	}, 10000);
}

startPlay()

boxee.onPause = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}

boxee.onPlay = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}
