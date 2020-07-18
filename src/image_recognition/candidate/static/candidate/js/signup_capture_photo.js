document.addEventListener("DOMContentLoaded", function() {

  var width = 640;    // We will scale the photo width to this
  var height = 480;     // This will be computed based on the input stream


  var ele_result_snapshot = document.getElementById('result-snapshot');
  
  Webcam.set({
    width: width,
    height: height,
    image_format: 'jpeg',
    jpeg_quality: 90,
    // flip_horiz: true,
  });
  Webcam.attach( '#camera' );
  
  function take_snapshot() {
    // take snapshot and get image data
    Webcam.snap( function(data_uri) {
      // display results in page
      ele_result_snapshot.src = data_uri

    });
  }
  
  function callback_append_new_img(){
      // append uploaded image
      $("#photo-gallery").append( 
        `<a data-fancybox="gallery" href="${ele_result_snapshot.src}">
              <img class="img-thumbnail" src="${ele_result_snapshot.src}">
          </a>`
      );
      console.log("photo appended to photo gallery in take_snapshot()")
      console.log($("#photo-gallery"));
  }

  function reset_upload_btn(){
    // reset upload button
    $("#btn-upload").button('reset');
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

      reset_upload_btn(); // remove processing icon

      if(code == 200){

          if(obj.success == 1)
          {
            console.info("Photo Uploaded Successfully.");
            new PNotify({
                title: 'Success',
                text: 'Photo Uploaded Successfully.',
                addclass: 'alert alert-styled-left alert-arrow-left',
                type: 'success'
            });

            callback_append_new_img();
          }
          else
          {
            console.error(obj.message.text);
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
        console.error("Error ... Problem while uploading file.")
      }
    });  
  }

  /**************************************************** */
  /*********** button click events ******************** */
  /**************************************************** */
  $(document).on("click", '#btn-capture', function(){
                
    console.log("#btn-capture button click event triggered");
    //take snapshot
    take_snapshot();

    $("#container-camera").fadeOut();
    $("#container-result").removeClass("hidden").addClass("fadeIn")
  });

  $(document).on("click", '#btn-upload', function(){
    console.log("#btn-upload button click event triggered");
    //upload snapshot
    saveSnap();
  });

  $(document).on("click", '#btn-cancel', function(){
    console.log("#btn-cancel button click event triggered");
    $("#container-result").addClass("fadeOut").addClass("hidden")
    $("#container-camera").fadeIn();
  });

});
