 // <!-- Send csrf token when making AJAX requests-->
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var editor;
    // Data Table
    $(document).ready(function() {
        $('#tabel-expirari').DataTable({
            stateSave: true,
            scrollCollapse: true,
            scrollY: '55vh',
            "lengthMenu": [[10, 25, 50, 100, 250], [10, 25, 50, 100, 250]],
              "columnDefs": [
                { "width": "8%", "targets": 0 }
              ]
        });  
    });



    // home.html scripts
    $(function(){

        //button send SMS
        $("#selected").click(function () {
            var items=[];
            $("input.select-item:checked:checked").each(function (index,item) {
                items[index] = item.value;
            });
            if (items.length < 1) {
                alert("Nu ati selectat niciun destinatar");
            }else {
                var msgId = $('#inputState').children(":selected").attr("value")
                $.ajax({
                    type: "POST",
                    url: '/sendSMS/',
                    data: {
                      'expirari-ids': JSON.stringify(items),
                      'msg-id': msgId, 
                    },
                    dataType: 'json',
                    success: function (data) {
                        location.reload();
                        // alert("Success! SMSurile au fost trimise");
                    }
                  });
            }
        });

        //button delete 
        $("#delete").click(function () {
            var items=[];
            $("input.select-item:checked:checked").each(function (index,item) {
                items[index] = item.value;
            });
            if (items.length < 1) {
                alert("Nu ati selectat nimic");
            }else {
                $.ajax({
                    type: "POST",
                    url: '/sendSMS/',
                    data: {
                      'Delete': 'True',
                      'expirari-ids': JSON.stringify(items)
                    },
                    dataType: 'json',
                    success: function (data) {
                        location.reload();
                    }
                  });
            }
        });

        //button select all or cancel
        $("#select-all").click(function () {
            var all = $("input.select-all")[0];
            all.checked = !all.checked
            var checked = all.checked;
            $("input.select-item").each(function (index,item) {
                item.checked = checked;
            });
        });


        //column checkbox select all or cancel
        $("input.select-all").click(function () {
            var checked = this.checked;
            $("input.select-item").each(function (index,item) {
                item.checked = checked;
            });
        });


         $("#inputState").change(function () {
            var id = $('#inputState').children(":selected").attr("title")
            $("#message-textarea")[0].value = id;
    });



});