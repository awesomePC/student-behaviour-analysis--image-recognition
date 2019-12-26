var arr_suspicious = [];

function handle_suspicious_activity(reason)
{
  // debugger;

  var length = arr_suspicious.length;
  // get 
  // check array length >= suspicious 
  if ( length >= suspicious_show_warning_after)
  {
    var is_continuous_suspicious = true;
    
    var warning_limit = suspicious_show_warning_after - 1

    for (index = warning_limit; index >= 0 ; index--) { 
        // console.log(arr_suspicious[index]); 
        if(arr_suspicious[index] == false)
        {
          is_continuous_suspicious = false;
        }
    } 

    if(is_continuous_suspicious)
    {
      // show warning
      new PNotify({
          title: "Warning",
          text: "Suspicious activity - " + reason,
          addclass: 'alert alert-styled-left alert-arrow-left',
          type: "warning"
      })
    }
  }

  // check limit of suspicious activity to stop exam 
  if ( length >= suspicious_stop_exam_after)
  {
    var is_continuous_suspicious = true;
    
    var stop_limit = suspicious_stop_exam_after - 1

    for (index = stop_limit; index >= 0 ; index--) { 
        // console.log(arr_suspicious[index]); 
        if(arr_suspicious[index] == false)
        {
          is_continuous_suspicious = false;
        }
    } 

    if(is_continuous_suspicious)
    {
      // stop exam
      $.ajax({
          data: {
              "exam_id": exam_id,
              "exam_candidate_id": exam_candidate_id,
              "reason": reason,
          },
          method: "POST",
          url: url_stop_exam,

      }).done(function(data) {
          // If successful
          console.log(data);

      }).fail(function(jqXHR, textStatus, errorThrown) {
          // If fail
          console.log(textStatus + ': ' + errorThrown);
      });

      // url redirect to show reason of exam stop
      setTimeout(function(){
        // similar behavior as an HTTP redirect
        window.location.replace(url_stop_exam_reason);
      }, 2000);

    }
  }
}


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


document.addEventListener("DOMContentLoaded", function() {

  var width = 640;    // We will scale the photo width to this
  var height = 480;     // This will be computed based on the input stream

  var base64image = null;

  Webcam.set({
    width: width,
    height: height,
    image_format: 'jpeg',
    jpeg_quality: 90,
    // flip_horiz: true, // mirror mode
  });
  Webcam.attach( '#camera' );

  
  // Save Image
  /*
  The method takes 3 parameters –
  
  Generated base64 value
  Action URL ( for handling the value and saving to the directory )
  Callback function ( For handling response )
  */
  function takeSaveRecognizeSnap(){

    // take snapshot and get image data
    Webcam.snap( function(data_uri) {
      base64image = data_uri
    });
    
    var url = url_save_recognize_exam_photo;

    Webcam.upload( base64image, url, function(code, data) {
      // console.log(code);
      console.log(data);

      if(code == 200){
        var obj_data = jQuery.parseJSON(data);
        is_suspicious = obj_data.is_suspicious

        arr_suspicious.push(is_suspicious)

        if(is_suspicious == true)
        {
          handle_suspicious_activity(
            obj_data.reason
          )
        }
      }
      else
      {
        console.log(code);
        console.log("Error ... Problem while uploading file.")
      }
    });  
  }

  async function process_recognition()
  {
    await sleep(capture_image_time);

    // infinite loop
    while (true) {
      takeSaveRecognizeSnap();

      console.log('Taking a break...');
      await sleep(capture_image_time);
    }
  }

  /**
   *  Capture and send image to server 
   *  Recognize image
   *  Detect illegal activity
   */
  Webcam.on('live', function() {
    // camera is live, showing preview image
    // and user has allowed access
    console.log("webcam started");

    // start processing
    process_recognition();
  });

  /**
   *  Show live recording 
   */
  Webcam.on('live', function() {
    setInterval(function(){
      // take snapshot and get image data
      Webcam.snap( function(data_uri) {
        // display results in page
        $("#live-img").attr("src", data_uri);
      });
    }, 200);
  });
  

  /**
   * Fires when an error occurs 
   * (your callback function is passed an error string).
   */
  Webcam.on( 'error', function(err) {
    // an error occurred (see 'err')
    console.log(err);
  } );
  
});
