// Define Global Array to GET request
let ingredients = [];


// Dropdown ingredient suggestions after DOMloaded
document.addEventListener("DOMContentLoaded", function(){
    
    // Listen to input and ask server for /ingredients
    $( async function call_array() {
        let response = await fetch('/ingredients');
        let array = await response.json();
        var suggestions = array;
        $("#ingredients").autocomplete({
            source: suggestions
        });
    });
    

});


// Clear all values
function clear_inputs(){

    window.onbeforeunload = function(){

        var filters_elems = document.querySelectorAll('#quit-filter');
        filters_elems.forEach(function(item) {
            item.parentElement.remove();
        });

        document.getElementById('q').value = null;

        while(ingredients.length) {
            ingredients.pop();
        }

    }
}


// Check for duplicates in selected ingredients
function duplicate(word) {
    for (i = 0; i < ingredients.length; i++)
    {
        if(ingredients[i] == word) {
            return 1;
        }
    }
    return 0;
}


// Add filters and pass them through get method
function add_ingredient() {

    // Store value
    let ing = document.querySelector('#ingredients').value;

    // Reset input form
    document.querySelector('#ingredients').value = "";

    // Call latest ingredients table from SQL db
    async function call_array(){
        let response = await fetch('/ingredients');
        let array = await response.json();

        // Iterate through each ingredient to check validity
        let flag = 0;
        let count = 0;
        for (let row in array) {
            // Check for duplicates
            if(duplicate(ing)) {
                alert('You already have that ingredient!');
                break;
            }
            // If ingredient is valid, proceed to add it as a filter
            if(array[row] == ing) {
                // Add elemento to the Array
                ingredients.push(ing);
                // Print elemento into html page
                last = ingredients.length - 1;
                document.querySelector('#filters').innerHTML += '<li class="list-inline-item badge rounded-pill bg-secondary mx-2" style="font-size:medium;">' + ingredients[last] + '<button type="button" class="btn-close ms-1 h6" id="quit-filter" aria-label="Close"></button></li><span class="bg-white">&nbsp&nbsp</span>';
                // Write all the filters in the input form to do GET request
                if(ingredients){
                    document.querySelector("#q").value = ingredients;
                    flag = 1;
                    break;
                }
            }
            count++;
        }
        // If counter reach to the end of array prompt NOT VALID
        if (flag == 0 && (count == array.length)) {
            alert('Please Type an Ingredient from the suggested list');
        } 
        
        let filters = document.querySelectorAll("#quit-filter");
        filters.forEach(function(item) {
            item.addEventListener('click', function(e) {
                let filter = item.parentElement.innerText;
                for (let i = 0; i < ingredients.length; i++) {
                    if (ingredients[i].localeCompare(filter) == 0) {
                        ingredients.splice(i, 1);
                        document.querySelector("#q").value = ingredients;
                    }
                }
                item.parentElement.remove();
            });
        });
    }
    call_array();


}


function validate_user() {
    //alert(document.getElementById('user').value);
    if ( /([^\w])/g.test(document.getElementById('user').value) ) { // w reference to word, which is equivalent to [a-zA-Z_0-9] alphanumeric + underscore (_)
        alert("Please enter only valid characters (letters or numbers or underscore)");
        document.getElementById("user").value = "";
        document.getElementById("user").focus();
    }
}


function validate_pass() {
    if ( document.getElementById('pass').value.length < 8 ) { 
        $("#pass_msg").text("Password must be 8 character length ");
        document.getElementById("pass").value = "";
    }
    else if ( ! /[!#@$%^&*.,?-_]/g.test(document.getElementById('pass').value) ) {
        $("#pass_msg").text("Password must have a special character ! # @ $ % ^ & * . , ? - _"); // ([^\w])([\/\\#$%^&*.,?"\[])
        document.getElementById("pass").value = "";
    }
    else if ( ! /[a-z]/g.test(document.getElementById('pass').value) ) {
        $("#pass_msg").text("Password must have at least one letter");
        document.getElementById("pass").value = "";
    }
    else if ( ! /[A-Z]/g.test(document.getElementById('pass').value) ) {
        $("#pass_msg").text("Password must have at least one capital letter");
        document.getElementById("pass").value = "";
    }
    else if (! /[0-9]/g.test(document.getElementById('pass').value)) {
        $("#pass_msg").text("Password must be have at least one number");
        document.getElementById("pass").value = "";
    }
    else {
        $("#pass_msg").text("");
    }
}


function validate_confirmation() {
    $("#pass, #pwconf").keyup(function (e) { 
        if( $("#pass").val() != $("#pwconf").val() ) {
            $("#pwconf_msg").removeClass("text-success");
            $("#pwconf_msg").addClass("text-danger");
            $("#pwconf_msg").text("Password do not match!");
            $("#pwconf").removeClass("text-success");
            $("#pwconf").addClass("text-danger");
        }
        else {
            $("#pwconf_msg").removeClass("text-danger");
            $("#pwconf_msg").addClass("text-success");
            $("#pwconf_msg").text("Password Correct");
            $("#pwconf").removeClass("text-danger");
            $("#pwconf").addClass("text-success");
        }
    });
}


function add_bookmark(id) {
    $.ajax({ 
        url: '/add_bookmark?id='+id, 
        type: 'GET', 
        success: function(response){ 
            $('#'+response).attr('onclick','drop_bookmark('+response+');');
        } 
    })
}


function drop_bookmark(id) {
    $.ajax({ 
        url: '/drop_bookmark?id='+id, 
        type: 'GET', 
        success: function(response){ 
            $('#'+response).attr('onclick','add_bookmark('+response+');');
        } 
    })
}

// Back color change to notice when sth is being dropped.
function dropColor(ev) {
    ev.preventDefault();
    document.getElementById('drop-area').style.backgroundColor = '#BBD5B8';
}


// Allow to drop sth on element preventing default which is get to link when sth is drop.
function allowDrop(ev) {
    ev.preventDefault(); 
}


// Drop data and retrieve it to the server.
function drop(ev) {
    ev.preventDefault(); //default is open as link on drop
    var image = ev.dataTransfer.files;
    text = ev.target.appendChild(document.createElement('p'));
    text.innerHTML = "Image loaded";
    document.getElementById('input-hidden').files = image;
}


/* DROP FUNCTION WITHOUT INPUT FORM - AJAX POST METHOD
function drop(ev) {
    ev.preventDefault(); //default is open as link on drop
    var image = ev.dataTransfer.files;
    text = ev.target.appendChild(document.createElement('p'));
    text.innerHTML = "Image loaded";
    upload_image(image[0]);
}
function upload_image(image) {

    formImage = new FormData();
    formImage.append('file', image);
    console.log(image.name)
    
    /*document.getElementById('btn-upload').addEventListener('click', function(e) {
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formImage,
            enctype: 'multipart/form-data',
            contentType: false,
            cache: false,
            processData: false,
            success: function(response) {
                
            }
        });
    });
    
}*/

/* WORKING SOLUTION 
var aj = new XMLHttpRequest();
    aj.onreadystatechange = function() {
        if (aj.readyState == 4 && aj.status == 200) {
            alert("it worked")
        }
    };
    aj.open("POST","/upload", true);
    formImage = new FormData();
    formImage.append('file', $('#upload-file')[0]);
    aj.send(formImage);
*/
    /*//document.getElementById('btn-upload').addEventListener('click', function(e) {
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formImage,
            enctype: 'multipart/form-data',
            contentType: false,
            cache: false,
            processData: false,
            success: function(response) {
                // TO DO
            }
        });
    //});*/
    
/*
function add_bookmark2(id) {
    var aj = new XMLHttpRequest();
    aj.onreadystatechange = function() {
        if (aj.readyState == 4 && aj.status == 200) {
            // do sth
        }
    };

    aj.open("GET","/add_bookmark", true);
    aj.send();
}
*/

//function validate_input() {
    //if not name or not password:
    //        return apology("Must provide valid username/password")
    //    elif password != confirmation:
    //        return apology("Password do not match")
//}

//search_button.addEventListener("click")
//async function fetch_ingredients() {
//    let response = await fetch('/search?q=' + ingredients);
//    let shows = await response.text();
//    document.querySelector('#filters').innerHTML = shows;
//}

/* These code to retrieve like was updated by loadlikes(int) function.
let posts = document.querySelectorAll('.post');
posts.forEach(function(item) {
    let postid = item.getAttribute('id');
    if (postid != null) {
        async function e() {
            let response = await fetch('/serv?q=' + postid);
            let array = await response.json();
            var post_likes = array;
            document.getElementById(`${postid}.heart`).innerHTML = post_likes.likes;
        }
        e();
    }
});
*/

/* This piece of code was updated to use a jquery much user friendly autocomplete from jquery documentation!
let input = document.getElementById('ingredients');
input.addEventListener('keyup', async function() {
    // Suggest List
    let response = await fetch('/suggest?q=' + input.value);
    let ings_from_server = await response.json();
    let html = '';
    for (let row in ings_from_server) {
        let ing = ings_from_server[row].ingredients;
        html += '<option value=' + ing + '>';
    }
    document.getElementById('suggest').innerHTML = html;
});
*/

/* This part was updated because it works but ramdomly returns cookie error because of @app.template response + fetch
// Load post likes
async function loadlikes(id) {
    let response = await fetch('/serv?p='+id);
    let post_likes = await response.text();
    document.getElementById(`${id}.heart`).innerHTML = post_likes;
}

// Load favourites
async function isfavourite(id) {
    let response = await fetch('/favs?f=' + id)
    let saved_recipes = await response.json();
    if (saved_recipes[0].recipes_id) {
        document.getElementById(`${id}`).checked = true;
    }
    else { 
        document.getElementById(`${id}`).checked = false;
    }
}
*/