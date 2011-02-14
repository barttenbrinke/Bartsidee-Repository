boxee.enableLog(true);
boxee.renderBrowser = true;
boxee.autoChoosePlayer = false;

hasActive = false;
hasSet = false;


_findPlayer = setInterval(function()
{
   if (!hasSet)
   {
      boxee.getWidgets().forEach(function(widget)
      {
         if (widget.getAttribute("id") == 'tpSwf')
         {
            boxee.renderBrowser=false;
            widget.setCrop(0, 0, 0, 45);
            boxee.notifyConfigChange(widget.width, widget.height-45);
            widget.setActive(true);
            boxee.setCanPause(true);
            boxee.setCanSkip(false);
            boxee.setCanSetVolume(false);
			hasSet = true;
            clearInterval(_findPlayer);
			setTimeout(function() {boxee.getActiveWidget().click(25,380);}, 4000);
			
         }
      });
   }
}, 1000);

function startPlay()
{
	boxee.getActiveWidget().click(25,380);
}   
   
boxee.onPause = function()
{
//OK
   boxee.getActiveWidget().click(25,380);
}
 
boxee.onPlay = function()
{
//OK
   boxee.getActiveWidget().click(25,380);
}