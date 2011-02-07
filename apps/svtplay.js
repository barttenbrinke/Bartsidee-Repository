boxee.setDefaultCrop(0,0,0,28);

if(boxee.getVersion() > 3.0)
{
  boxee.setCanPause(true);
  boxee.setCanSkip(false);
  boxee.setCanSetVolume(false);
}

boxee.onPause = function() {
	boxee.getActiveWidget().click(16,375);
}
boxee.onPlay = function() {
	boxee.getActiveWidget().click(16,375);
}
