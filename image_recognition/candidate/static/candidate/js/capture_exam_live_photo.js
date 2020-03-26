var arr_suspicious = [];

// check all values are true - 
const isAllTrue = (currentValue) => currentValue == true;

function handle_suspicious_activity(reason)
{
  /**** check suspicious activity for showing warning ***************/
  // get last elements from arr-suspicious list
  var sliced_data = arr_suspicious.slice(-suspicious_show_warning_after); // get last two elements

  // The every() method tests whether all elements in the array pass the 
  // test implemented by the provided function. It returns a Boolean value.
  var result = sliced_data.every(isAllTrue);

  if (result == true)
  {
    // show warning
    new PNotify({
        title: "Warning",
        text: "Suspicious activity - " + reason,
        addclass: 'alert alert-styled-left alert-arrow-left',
        type: "warning"
    })
  }


  // The every() method tests whether all elements in the array pass the 
  // test implemented by the provided function. It returns a Boolean value.
  var result = sliced_data.every(isAllTrue);
  
  if (result == true)
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


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


var width = 640;    // We will scale the photo width to this
var height = 480;     // This will be computed based on the input stream

var base64image = null;

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

document.addEventListener("DOMContentLoaded", function() {

  Webcam.set({
    width: width,
    height: height,
    image_format: 'jpeg',
    jpeg_quality: 90,
  });
  Webcam.attach( '#camera' );


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
