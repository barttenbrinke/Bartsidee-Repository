boxee.enableLog(true);
boxee.autoChoosePlayer=false;
boxee.renderBrowser=true;

boxee.onInit = function() {
   browser.setCookie(".bbc.co.uk", "BBCPGstat", "0%3A-");
   browser.setCookie("empsize=large&ia=1");
}

var btn_y = 374;

var btn_x1 = 16;
var btn_x2 = 722;
var btn_x3 = 560;

var hasActive=false;
var Rescale=false;
var Subtitle=true;

if (boxee.getVersion() > 3.0)
{
	boxee.setCanPause(true);
	boxee.setCanSkip(false);
	boxee.setCanSetVolume(false);
}

function poll()
{
	if (!hasActive)
	{
		boxee.getWidgets().forEach(function(A)
		{
			if (A.width == 640 && A.height == 395 && A.getAttribute("src") != -1)
			{
				if(!Rescale)
				{
					setTimeout(largeScale, 2000);
					boxee.renderBrowser=true;
					Rescale=true;
					poll();
				}
				else
				{
					hasActive=true;
					btn_y = 374; 
					btn_x2 = 505;
					boxee.renderBrowser=false;
					A.setActive(true);
					boxee.notifyConfigChange(A.width,A.height);
					setTimeout(startPlay, 2800);
				}
			}
			else if (A.width == 832 && A.height == 503 && A.getAttribute("src") != -1)
			{
				hasActive=true;
				btn_y = 482;
				btn_x2 = 697;				
				boxee.renderBrowser=false;
				A.setActive(true);
				boxee.notifyConfigChange(A.width,A.height);
				setTimeout(startPlay, 2800);
			}
		});
	}
}

setInterval(poll,1000);


function startPlay()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
	setTimeout(function() {if(Subtitle)
		{
			boxee.getActiveWidget().click(btn_x2,btn_y);
		}
	}, 10000);
}

function largeScale()
{
	boxee.getActiveWidget().click(btn_x3,btn_y);
}

boxee.onPause = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}

boxee.onPlay = function()
{
	boxee.getActiveWidget().click(btn_x1,btn_y);
}
