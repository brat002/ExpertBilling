function checkCookie(array_name) {
	var index_id = ["user-info", "news-cell", "account_information", "traffic", "prepaid_traffic", "tariffs" ];
	var statistics = ["transactions_data", "active_session_data", "periodical_service_history_data", "one_time_history_data", "addon_service_transaction_data", "traffic_transaction_data"];
	eval('curent_array = '+array_name);
	for (i = 0; i < curent_array.length; i++) {
		cookie_value = $.cookie(curent_array[i])
		if (cookie_value == 'hide') {
			runEffect(curent_array[i]);
		} 	
	}
}
