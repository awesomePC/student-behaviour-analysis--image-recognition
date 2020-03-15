document.addEventListener("DOMContentLoaded", function() {

  var width = 1024;    // We will scale the photo width to this
  var height = 768;     // This will be computed based on the input stream


  var ele_result_snapshot = document.getElementById('result-snapshot');
  
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
  function saveSnap(){
    var base64image = ele_result_snapshot.src;
    
    var url = url_save_captured_sign_up_photo;

    Webcam.upload( base64image, url, function(code, text) {
      console.log(code);
      console.log(text);
      
      var obj = jQuery.parseJSON(text)

      if(code == 200){
          if(obj.success == 1)
          {
            new PNotify({
                title: 'Success',
                text: 'Photo Uploaded Successfully.',
                addclass: 'alert alert-styled-left alert-arrow-left',
                type: 'success'
            });
          }
          else
          {
            new PNotify({
                title: obj.message.title,
                text: obj.message.text,
                addclass: 'alert alert-styled-left alert-arrow-left',
                type: obj.message.type
            }); 
          }
      }
      else
      {
        console.log("Error ... Problem while uploading file.")
      }
    });  
  }

  /**************************************************** */
  /*********** button click events ******************** */
  /**************************************************** */
  $(document).on("click", '#btn-capture', function(){
    //take snapshot
    take_snapshot();
    new PNotify({
      title: 'Photo Captured',
      text: 'Scroll down to see captured photo.',
      addclass: 'alert alert-styled-left alert-arrow-left',
      type: 'info'
    });

    $("#container-camera").fadeOut();
    $("#container-result").removeClass("hidden").addClass("fadeIn")
  });

  $(document).on("click", '#btn-upload', function(){
    //upload snapshot
    saveSnap();
  });

  $(document).on("click", '#btn-cancel', function(){
    $("#container-result").addClass("fadeOut").addClass("hidden")
    $("#container-camera").fadeIn();
  });

});
