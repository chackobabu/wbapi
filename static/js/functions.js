function showselection_series() {
    if ($('#display_chosen').is(':visible')) {
        $('#display_chosen').prop('hidden', true);
        $('#show_hide_series').text('Show chosen series(s)')
    } else {
        $('#display_chosen').prop('hidden', false);
        $('#show_hide_series').text('Hide chosen series(s)')
    }
};
function showselection_economies() {
    if ($('#display_chosen_economies').is(':visible')) {
        $('#display_chosen_economies').prop('hidden', true);
        $('#show_hide_economies').text('Show chosen economies(s)')
    } else {
        $('#display_chosen_economies').prop('hidden', false);
        $('#show_hide_economies').text('Hide chosen economies(s)')
    }
};
function check_referrer() {
    if (document.referrer.includes('series')) {
        $('a.ref').attr('href', 'http://127.0.0.1:5000/select_series')
        $('a.ref').text('Go back to choose series');
    } else if (document.referrer.includes('economies')) {
        $('a.ref').attr('href', 'http://127.0.0.1:5000/economies')
        $('a.ref').text('Go back to choose economies');
    }
};



$(document).ready(function () {
    check_referrer()
    //select all button
    $('#select_all').on('change', function () {
        $('.select_series li:visible input').prop('checked', $('#select_all').prop('checked'));
        if ($('.select_series li:visible input:checked').length == $('.select_series li:visible').length) {
            $('label[for="select_all"]').text(' Deselect All');
        } else {
            $('label[for="select_all"]').text(' Select All');
        }
    });

    function update_count() {
        $('#count_countries').text($('.select_series li input:visible').length);
    };

    //searchbar function - defining
    // function search_bar() {
    //     var search_terms = $.map($('#searchBar').val().toLowerCase().split(','), $.trim);
    //     $('.select_series li').each(function () {
    //         var choice = $(this).find('input').attr('id').toLowerCase().trim();
    //         var region_choice = $(this).find('input').attr('data-region').toLowerCase().trim();
    //         var incLevel_choice = $(this).find('input').attr('data-income').toLowerCase().trim();
    //         if (choice.match(search_terms.join('|')) && region_choice.match(region_filters.join('|')) && incLevel_choice.match(income_filters.join('|'))) {
    //             $(this).show();
    //         } else {
    //             $(this).hide();
    //         }
    //     });
    //     update_count();
    // }

    function searchbar(type) {
        if (type == "series") {
            var search_terms = $.map($('#searchBar_series').val().toLowerCase().split(','), $.trim);
            $('.select_series li').each(function () {
                var choice = $(this).find('input').attr('id').toLowerCase().trim();
                if (choice.match(search_terms.join('|'))) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });

        } else if (type == 'economies') {
            console.log("economies_search")
            var search_terms = $.map($('#searchBar_economies').val().toLowerCase().split(','), $.trim);
            $('.select_series li').each(function () {
                var choice = $(this).find('input').attr('id').toLowerCase().trim();
                var region_choice = $(this).find('input').attr('data-region').toLowerCase().trim();
                var incLevel_choice = $(this).find('input').attr('data-income').toLowerCase().trim();
                if (choice.match(search_terms.join('|')) && region_choice.match(region_filters.join('|')) && incLevel_choice.match(income_filters.join('|'))) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
            update_count();
        }
    }

    //display selected countries in a box below
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
        $('.display_selected p').text("Selected: (" + selected.length + ")");
        selected.forEach(function (id) {
            displayList.append('<li style="display:inline;">' + id + ', </li>');
        });
    });

    //region and income level filters
    var region_checkboxes = $('.filter_region li input[type="checkbox"]');
    var inclevel_checkboxes = $('.filter_inc_level li input[type="checkbox"]');

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
        update_count();
        searchbar(type="economies");
        region_re = region_filters.join('|')
        income_re = income_filters.join('|')
        $('.select_series li:visible').each(function () {
            var region_choice = $(this).find('input').attr('data-region').toLowerCase().trim();
            var incLevel_choice = $(this).find('input').attr('data-income').toLowerCase().trim();
            if (region_filters.length > 0 && income_filters.length > 0) {
                if (region_choice.match(region_re) && incLevel_choice.match(income_re)) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            } else if (region_filters.length > 0 && income_filters.length == 0) {
                if (region_choice.match(region_re)) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            } else if (region_filters.length == 0 && income_filters.length > 0) {
                if (incLevel_choice.match(income_re)) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            }
        });
    });

    //the search bar
    $("#searchBar_economies").on('keyup', function () {
        searchbar(type = 'economies');
    });

    $("#searchBar_series").on('keyup', function () {
        searchbar(type = 'series');
    });
});