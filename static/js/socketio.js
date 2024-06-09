document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    socket.on('connect', () => {
        console.log('Connected to Socket.IO server');
        socket.send("hello from client!");
    });

    socket.on('alert-event', data => {
        console.log(data)
    });
})