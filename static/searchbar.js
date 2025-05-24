jQuery(document).ready(function($){

$('.live-search-list tr').each(function(){
$(this).attr('data-search-term', $(this).text().toLowerCase());
});

$('.live-search-box').on('keyup', function(){

var searchTerm = $(this).val().toLowerCase();

    $('.live-search-list tr').each(function(){
        if (searchTerm.length == 0 || $(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0) {
            $(this).show();
        } else {
            $(this).hide();
        }

    });

});

});