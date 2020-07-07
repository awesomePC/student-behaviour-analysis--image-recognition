
// question id from table
var current_question_id = null;
// question sequence number
var current_question_index = null;
var prev_question_index = null;

var question = null;
var is_continue_exam = true;


function handle_question_info(data)
{
    // debugger;
    var ele_question_title = $("#question-title").get(0)
    var ele_question_number =$("#question-number").get(0)
    var ele_question_options = $("#question-options").get(0)

    if (data.success == true){
        question = data.question;

        $(ele_question_number).text(question.sequence)
        
        current_question_id = question.id;

        if (question.is_html ==true)
        {
            $(ele_question_title).html(question.title)
        }
        else
        {
            $(ele_question_title).text(question.title);
        }

        // options
        options = data.options;

        // clear previous all options
        $(ele_question_options).html("");

        $.each(options, function( index, option ) {
            var ele_option = null;
            if (question.is_multi_answer == true)
            {
                // render options as checkbox
                ele_option = $(`<div class="checkbox">
                    <label>
                        <input type="checkbox" value="${option.sequence}">
                        <span>${option.title}</span>
                    </label>
                </div>`);
            }
            else
            {
                // render options as radio-button
                ele_option =  $(`
                    <div class="radio">
                        <label>
                            <input type="radio" value="${option.sequence}" name="radio-styled-color" class="control-warning">
                            ${option.title}
                        </label>
                    </div>
                `);

            }

            // check is user selected it (If this question repeated traversed by user)
            if (option.is_selected_by_user)
            {
                $(ele_option).find("input").attr("checked", "checked");
            }

            // append element
            $(ele_question_options).append(ele_option);

        });

        // init uniform
        $("input").uniform({
            radioClass: 'choice',
            wrapperClass: 'border-info-600 text-info-800'
        });
    }
    else
    {
        console.log(data.success)
    }
}


function get_question_info(question_id)
{
    $.ajax({
        data: {
            "question_index": question_id,
            "exam_id": exam_id,
        },
        method: "POST",
        // dataType: 'json',
        url: '/exam/get_question_info/'

    }).done(function(data) {
        // If successful
        console.log(data);
        // handle data
        handle_question_info(data);

    }).fail(function(jqXHR, textStatus, errorThrown) {
        // If fail
        console.log(textStatus + ': ' + errorThrown);
    });

}

function handle_next_action_needed(data)
{
    if("next_action_needed" in data)
    {
        next_action_needed = data.next_action_needed

        if("show_msg" in next_action_needed)
        {
            new PNotify({
                title: 'Info',
                text: next_action_needed.show_msg.text,
                addclass: 'alert alert-styled-left alert-arrow-left',
                type: next_action_needed.show_msg.type
            });
        }
        if("redirect" in next_action_needed)
        {
            var redirect_url = next_action_needed.redirect.url;
            var timeout = next_action_needed.redirect.timeout;

            setTimeout(function(){
                location.href = redirect_url;
            }, timeout)
        }
    }
}

function get_next_question_index(param_data)
{
    $.ajax({
        data: param_data,
        method: "POST",
        url: '/candidate/get_next_question_index/'

    }).done(function(data) {
        // If successful
        console.log(data);

        if(data.message.type == "success")
        {
            next_question_index = data.next_question_index

            get_question_info(question_sequence=next_question_index)
        }
        else
        {
            handle_next_action_needed(data);
        }

    }).fail(function(jqXHR, textStatus, errorThrown) {
        // If fail
        console.log(textStatus + ': ' + errorThrown);
    });

}

function save_and_next()
{
    var ele_question_number =$("#question-number").get(0)
    var ele_question_options = $("#question-options").get(0)

    current_question_index = parseInt($(ele_question_number).text())

    var arr_sel_opt_values = [];
    $(ele_question_options).find('input').each(function(){
        
        if($(this).is(':checked'))
        {
            var selected_value = parseInt(
                $(this).val()
            )

            if(Number.isInteger(selected_value))
            {
                // checked
                arr_sel_opt_values.push(
                    selected_value
                );
            }
            else
            {
                console.log("Error .. Pushing value in array .. the value is not numeric")
                console.log(selected_value)
            }
        }
        else
        {
            // unchecked
        }
    });

    console.log("arr_sel_opt_values :", arr_sel_opt_values)
    // alert(arr_sel_opt_values)
    
    if (typeof arr_sel_opt_values !== 'undefined' && arr_sel_opt_values.length > 0) {

        // str_selected_options = arr_sel_opt_values.toString()

        $.ajax({
            data: {
                "question_id": current_question_id,
                "exam_candidate_id": exam_candidate_id,
                "arr_sel_opt_values": arr_sel_opt_values,
            },
            method: "POST",
            // dataType: 'json',
            url: '/candidate/save_candidate_answer/'
    
        }).done(function(data) {
            // If successful
            console.log(data);

            // get next question data
            var param_data = {
                "exam_id": exam_id,
                "prev_question_index": current_question_index,
            }
            get_next_question_index(
                param_data
            )

            // Mark question pallet number as saved // add green bg
            $("#question_pallete").find(`span[data-que-sequence='${current_question_index}']`).addClass("bg_light_green");
    
        }).fail(function(jqXHR, textStatus, errorThrown) {
            // If fail
            console.log(textStatus + ': ' + errorThrown);
        });
    }
    else
    {
        // get next question without saving
        var ele_question_number =$("#question-number").get(0);
        current_question_index = parseInt($(ele_question_number).text());
    
        get_question_info(current_question_index + 1);
    }
}

function submit_exam(){
    $.ajax({
        data: {
            "exam_id": exam_id,
        },
        method: "POST",
        url: '/candidate/submit_exam/'

    }).done(function(data) {
        // If successful
        console.log(data);
        
        new PNotify({
            title: data.message.title,
            text: data.message.text,
            addclass: 'alert alert-styled-left alert-arrow-left',
            type: data.message.type
        })

        handle_next_action_needed(data);

    }).fail(function(jqXHR, textStatus, errorThrown) {
        // If fail
        console.log(textStatus + ': ' + errorThrown);
    });
}

$(document).on("click", "#clear-response", function(){
    $(ele_question_options).find('input').each(function () {
        $(this).prop('checked', false);
    });
});


$(document).on("click", "#next", function(){
    var ele_question_number =$("#question-number").get(0);
    current_question_index = parseInt($(ele_question_number).text());

    get_question_info(current_question_index + 1);
});

$(document).on("click", "#save-and-next", function(){
    save_and_next();

    //
    // save photo
    takeSaveRecognizeSnap();
});

$(document).on("click", "#submit-exam", function(){
    submit_exam();
});


$(document).ready(function() {
    // ------------------------------------------------------
    // run as default 
    var param_data = {
        "exam_id": exam_id
    }
    get_next_question_index(
        param_data
    )

});