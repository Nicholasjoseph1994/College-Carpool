var state = {};
						    
		    onOpened = function() {
				connected = true;
			};
			      
			onMessage = function(m) {
				alert(state.token + " received " + m);
				updateNotifications();
			};
			
			updateNotifications = function() {
				state.notification_count += 1;
				$("#notification_count").html(state.notification_count);
			};
			
$(document).ready(function() {
	alert("got here");
	state = { 
		username: '{{ username }}',
		token: '{{ token }}',
		notification_count: '{{ notification_count }}'
	};
	
		    if (state.token) {
			    var channel = new goog.appengine.Channel(state.token);
			    var handler = {
				   'onopen': onOpened,
				   'onmessage': onMessage
				};
		  		var socket = channel.open(handler);
			    socket.onopen = onOpened;
			    socket.onmessage = onMessage;
			    socket.onerror = function(e){
	                alert("error:"+e['description']);
	            };
	            socket.onclose = function(){
	                alert("close");
	            };
		    }
};