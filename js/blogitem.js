function checkBolder(val) {
    if (val) {
       $('#preview_comment_button').css('font-weigh', 'bold');
    }
    return false;
}

function requireCaptcha(f) {
  if (!$('input[name="captcha_number"]', f).val()) {
    $('#captchas:hidden').show();
    //alert("To prove that you're not a spam robot, please verify the captcha image");
    return false;
  } else if ($('#captchas:hidden').size()) {
    $('#captchas:hidden').show();
  } else {
    return true;
  }
}

function __fillInForm(f, details) {
  var name = details[0];
  var email = details[1];
  var hide_email = parseInt(details[2]);
  var xsrf = details[3];

  if (name) $('input[name="name"]', f).val(name);
  if (email) $('input[name="email"]', f).val(email);
  if (hide_email) $('input[name="hide_email:boolean"]', f).attr('checked','checked');
  if (xsrf) $('input[name="xsrf"]', f).val(xsrf);
}


$(function() {

   var _got_comment_cookie=false;
   function _get_commit_cookie() {
      $.get('/getCommentCookie', {rnd:Math.random()}, function(resp) {
         if (resp && resp.split('|').length >3) {
            __fillInForm(f, resp.split('|'));
         }
      });
   }

   var f = $('#addcommentform');
   if ($('input[name="name"]', f).val() == ''
       && $('input[name="email"]', f).val() == ''
       && $('input[name="xsrf"]', f).val() == '') {
      f.fadeTo(0, 0.3).bind('mouseover', function() {
         $(this).unbind('mouseover').fadeTo(400, 1.0);
         if (_got_comment_cookie) return;
         _got_comment_cookie = true;
         _get_commit_cookie();
      });

      $(window).bind('scroll', function() {
         $(window).unbind('scroll');
         if (_got_comment_cookie) return;
         f.fadeTo(400, 1.0);
         _got_comment_cookie = true;
         _get_commit_cookie();

      });

   }

  $('textarea[name="comment:text"]').bind('keydown', function() {
    if ($(this).val()) {
      $('#preview_comment_button').css('font-weight', 'bold');
      $(this).unbind('keydown');
    }
  }).bind('change', function() {
    $('#captchawarning:hidden').show();
  });

  $('#add_comment_button').click(function() {
    var form = $(this).parents('form');
    if (!$.trim($('textarea', form).val())) {
      return false;
    }
    if (requireCaptcha(form)) {
      $(this).val('Adding comment...');
      return true;
    } else {
      return false;
    }
  });

   $('a.reply').click(function() {
      $('div.commentpreview').remove();
      var replypath, parent = $(this).parents('div.comment').eq(0);
      if (-1 < $(this).attr('href').indexOf('?')) {
         replypath = $(this).attr('href').split('=')[1].split('#')[0];
      } else {
         replypath = $(this).attr('href').split('#reply')[1];
      }
      $('#addcommentform').detach().insertAfter($('.commenttext', parent).eq(0));
      if (!$('#addcommentform input[name="replypath"]').size()) {
         $('#addcommentform').append($('<input name="replypath" type="hidden"/>').val(replypath));
      } else {
         $('#addcommentform input[name="replypath"]').val(replypath);
      }
      return false;
   });

   $('#preview_comment_button').click(function() {
      var form = $(this).parents('form');
      $('div.commentpreview').remove();
      $.post('previewComment', {
         comment:$('textarea[name="comment:text"]', form).val(),
         name:$('input[name="name"]', form).val(),
         email:$('input[name="email"]', form).val(),
           hide_email:$('input[name="hide_email:boolean"]', form)[0].checked
      }, function(response) {
         if (response && response.length) {
            $('<div></div>').addClass('commentpreview').html(response).insertBefore(form);
         }
      });

      return false;
   });

   $('form#addcommentform').submit(function() {
      if (!$.trim($('textarea', this).val())) {
         return false;
      }
      return true;
   });

   if (-1 != window.location.hash.search(/#comment-added/)) {
      $('#centercontent').prepend($('<div>Comment added! Thanks</div>').addClass('commentaddedmsg'));

      $('div.commentaddedmsg').click(function() {
         $(this).fadeOut(300);
         window.location.hash = '';
      });
      setTimeout(function() {
         $('div.commentaddedmsg:visible').fadeOut(900);
         //window.location.hash = '';
      }, 10* 1000);
   }

   if (location.hash.indexOf('#reply') == 0) {
      var id = location.hash.split('/')[location.hash.split('/').length-1];
      $('a.reply', '#' + id).click();
      window.location.hash = id;
   }
});