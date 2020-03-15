
// store 10 recognition result
var recognitions = [];

// counter to store how many images captured
var capture_count = 0;

// max_capture count
var max_capture_count = 3;

// capture image after 3 seconds
var seconds_2_wait = 10 * 1000;


function get_mode(arr){
  return arr.sort((a,b) =>
        arr.filter(v => v===a).length
      - arr.filter(v => v===b).length
  ).pop();
}

document.addEventListener("DOMContentLoaded", function() {

  var width = 1024;    // We will scale the photo width to this
  var height = 768;     // This will be computed based on the input stream


  var ele_result_snapshot = document.getElementById('video-snapshot');
  
  Webcam.set({
    width: width,
    height: height,
    image_format: 'jpeg',
    jpeg_quality: 90,
    flip_horiz: true,
  });
  Webcam.attach( '#camera' );
  
  function take_snapshot() {
    // take snapshot and get image data
    Webcam.snap( function(data_uri) {
      // display results in page
      ele_result_snapshot.src = data_uri
    });
  }
  
  // Save Image
  /*
  The method takes 3 parameters –
  
  Generated base64 value
  Action URL ( for handling the value and saving to the directory )
  Callback function ( For handling response )
  */
  function saveRecognizeSnap(){
    var base64image = ele_result_snapshot.src;
    
    var url = validation_url;

    Webcam.upload( base64image, url, function(code, data) {
      console.log(data);

      var obj_data = JSON.parse(data)

      if(code == 200){
        const photo = document.querySelector('#result_photo');
        photo.setAttribute('src', obj_data.img);

        if(obj_data.detected_face_count == 1)
        {
          // store is valid user
          recognitions.push(obj_data.is_authorized_candidate_present)
          console.log(recognitions)
        }
        else if(obj_data.detected_face_count > 1)
        {
          // push recognition false
          recognitions.push(false)

          new PNotify({
              title: "Warning",
              text: "Multiple persons detected in image",
              addclass: 'alert alert-styled-left alert-arrow-left',
              type: "warning"
          })
        }
        else
        {
          // push recognition false
          recognitions.push(false)

          new PNotify({
              title: "Warning",
              text: "No any person detected in image",
              addclass: 'alert alert-styled-left alert-arrow-left',
              type: "warning"
          })
        }
      }
      else
      {
        console.log(code);
        console.log("Error ... Problem while uploading file.")
      }
    });  
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function validate_user(){

    await sleep(5000); // before start

    while(capture_count < max_capture_count)
    {
      take_snapshot();
      saveRecognizeSnap();

      console.log('Taking a break...');
      // await sleep(10000);seconds_2_wait
      await sleep(seconds_2_wait);

      // increment counter to stop capturing images
      capture_count += 1;

      // check recognition array length size
      // if its equal to capture_count then proceed else don't increment
      if (recognitions.length != capture_count)
      {
        console.log("recognitions.length != capture_count so decrementing capture count")
        capture_count -= 1;
      }
    }

    await sleep(7000);
    console.log("Image capture and recognition completed");
    console.log(recognitions);

    console.log("Highest repeating value :")
    var mode = get_mode(recognitions);
    console.log(mode);

    $(".result-box").addClass("hidden");

    if(mode == true)
    {
      // user is valid user
      // user can proceed to exam
      $(".valid-candidate").removeClass("hidden");
    }
    else
    {
      // show error.. not valid user message with reasons
      $(".in-valid-candidate").removeClass("hidden");
    }

  }

  Webcam.on('live', function() {
    // camera is live, showing preview image
    // and user has allowed access
    console.log("webcam started");

    validate_user();
  })

  // (function loop() {
  //     var rand = Math.round(Math.random() * (3000 - 500)) + 2000;
  //     setTimeout(function() {
  //           //alert('A');
  //           take_snapshot();
  //           saveRecognizeSnap();
            
  //           loop();  

  //     }, rand);
  // }());
  
});
