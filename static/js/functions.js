// the search bar

function search_series() {
    var search_term = $('#searchBar').val().toLowerCase().trim();
    $('.select_series li').each(function () {
        var choice = $(this).find('input').attr('id').toLowerCase().trim();
        if (choice.match(search_term) || choice == search_term) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}

function showselection() {
    if ($('#chosen_series').is(':visible')){
        $('#chosen_series').prop('hidden',true);
    } else {
        $('#chosen_series').prop('hidden',false);  
    }    
}

function check_referrer() {
    if (document.referrer.includes('series')){
        $('a.ref').attr('href','http://127.0.0.1:5000/select_series')
        $('a.ref').text('Go back to choose series');
    } else if (document.referrer.includes('economies')){
        $('a.ref').attr('href','http://127.0.0.1:5000/economies')
        $('a.ref').text('Go back to choose economies');
}
};

$(document).ready(function () {

    check_referrer()
    // display selected fields on screen
    $('#select_all').on('change', function () {
        $('.select_series li:visible input').prop('checked', $('#select_all').prop('checked'));
    });

    var list = $('.select_series li input[type="checkbox"]');
    $('.select_series li input[type="checkbox"]').add('#select_all').on('change', function () {
        let selected = [];
        list.each(function () {
            if ($(this).prop('checked') == true) {
                selected.push($(this).attr('id'));
            }
        });
        var displayList = $('.display_selected ul');
        displayList.empty();
        $('.display_selected p').text("Your selection: (" + selected.length + ")");
        selected.forEach(function (id) {
            displayList.append('<li style="display:inline;">' + id + ', </li>');
        });
    });

    // region and income level filters
    var region_checkboxes = $('.filter_region li input[type="checkbox"]');
    var inclevel_checkboxes = $('.filter_inc_level li input[type="checkbox"]');

    // storing the checked filters in list
    let region_filters = [];
    region_checkboxes.on('change', function () {
        region_filters = [];
        region_checkboxes.each(function () {
            if ($(this).prop('checked') == true) {
                region_filters.push($(this).attr('id').toLowerCase().trim());
            }
            
        });
        console.log("Region filters:", region_filters);
    });

    // storing the income filters in list
    let income_filters = [];
    inclevel_checkboxes.on('change', function () {
        income_filters = [];
        inclevel_checkboxes.each(function () {
            if ($(this).prop('checked') == true) {
                income_filters.push($(this).attr('id').toLowerCase().trim());
            }
        });
        console.log("income filters:", income_filters);
    });

    region_checkboxes.add(inclevel_checkboxes).on('change', function () {
        region_re = region_filters.join('|')
        income_re = income_filters.join('|')

        $('.select_series li').each(function () {
            var region_choice = $(this).find('input').attr('data-region').toLowerCase().trim();
            var incLevel_choice = $(this).find('input').attr('data-income').toLowerCase().trim();

            if (region_filters.length >0 && income_filters.length >0) {
                if (region_choice.match(region_re) && incLevel_choice.match(income_re))  {
                    $(this).show();
                } else {
                    $(this).hide();
                }
                $('#count_countries').text($('.select_series li input:visible').length);

            }else if (region_filters.length >0 && income_filters.length == 0) {
                if (region_choice.match(region_re))  {
                    $(this).show();
                } else {
                    $(this).hide();
                }
                $('#count_countries').text($('.select_series li input:visible').length);
            }else if (region_filters.length == 0 && income_filters.length >0) {
                if (incLevel_choice.match(income_re))  {
                    $(this).show();
                } else {
                    $(this).hide();
                }
                $('#count_countries').text($('.select_series li input:visible').length);
            } else {
                $('.select_series li').each(function (){
                    $(this).show();
                });
                $('#count_countries').text($('.select_series li input:visible').length);
            }
        });
    });
});