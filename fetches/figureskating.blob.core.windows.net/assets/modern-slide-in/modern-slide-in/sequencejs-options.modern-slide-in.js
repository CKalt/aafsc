$(document).ready(function(){
    var options = {
        nextButton: true,
        prevButton: true,
        pagination: true,
        animateStartingFrameIn: true,
        autoPlay: true,
        autoPlayDelay: 6000,
        //preloader: true,
        //preloadTheseFrames: [1,2,3],
    };
    
    var mySequence = $("#sequence").sequence(options).data("sequence");
});