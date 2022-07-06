$.datetimepicker.setDateFormatter({
    parseDate: function (date, format) {
        var d = moment(date, format);
        return d.isValid() ? d.toDate() : false;
    },
    formatDate: function (date, format) {
        return moment(date).format(format);
    },
});

$('.datetime').datetimepicker({
    format:'DD-MM-YYYY hh:mm A',
    // format:'DD-MM-YYYY',
    formatTime:'hh:mm A',
    formatDate:'DD-MM-YYYY',
    useCurrent: false,
});

// Initialise Pusher
const pusher = new Pusher("32d695007f6b78ffea0d", {
    cluster: "us3",
    encrypted: true
});

var channel = pusher.subscribe('table');

channel.bind('new-record', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
   $('#jobs').append(`
        <tr id="${data.data.id}">
            <th scope="row"> ${data.data.job} </th>
            <td> ${data.data.eng} </td>
            <td> ${data.data.wip} </td>
            <td> ${data.data.hold} </td>
            <td> ${data.data.hrsn} </td>
            <td> ${data.data.qc} </td>
            <td> ${data.data.apr} </td>
            <td> ${data.data.qcn} </td>
            <td> ${data.data.model} </td>
        </tr>
   `)
});

channel.bind('update-record', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.job} </th>
        <td> ${data.data.eng} </td>
        <td> ${data.data.wip} </td>
        <td> ${data.data.hold} </td>
        <td> ${data.data.hrsn} </td>
        <td> ${data.data.qc} </td>
        <td> ${data.data.apr} </td>
        <td> ${data.data.qcn} </td>
        <td> ${data.data.model} </td>
    `)
 });





// channel.bind('new-record_mach', (data) => {
//     // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
//    $('#jobs').append(`
//         <tr id="${data.data.id}">
//             <th scope="row"> ${data.data.job} </th>
//             <td> ${data.data.eng} </td>
//             <td> ${data.data.wip} </td>
//             <td> ${data.data.hold} </td>
//             <td> ${data.data.hrsn} </td>
//         </tr>
//    `)
// });

channel.bind('update-record_mach', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.job} </th>
        <td> ${data.data.eng} </td>
        <td> ${data.data.wip} </td>
        <td> ${data.data.hold} </td>
        <td> ${data.data.hrsn} </td>
    `)
 });





channel.bind('new-record_tl', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
   $('#tjobs').append(`
        <tr id="${data.data.id}">
            <th scope="row"> ${data.data.job} </th>
            <td> ${data.data.mtl} </td>
            <td> ${data.data.mtln} </td>
            <td> ${data.data.pgm} </td>
            <td> ${data.data.pgmn} </td>
            <td> ${data.data.tlh} </td>
            <td> ${data.data.tlhn} </td>
        </tr>
   `)
});

channel.bind('update-record_tl', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.job} </th>
        <td> ${data.data.mtl} </td>
        <td> ${data.data.mtln} </td>
        <td> ${data.data.pgm} </td>
        <td> ${data.data.pgmn} </td>
        <td> ${data.data.tlh} </td>
        <td> ${data.data.tlhn} </td>
    `)
 });





channel.bind('new-record_bd', (data) => {
   $('#bendd').append(`
        <tr id="${data.data.id}">
            <th scope="row"> ${data.data.matl} </th>
            <td> ${data.data.desc} </td>
            <td> ${data.data.gauge} </td>
            <td> ${data.data.thick} </td>
            <td> ${data.data.rad} </td>
            <td> ${data.data.bd} </td>
            <td> ${data.data.pt} </td>
            <td> ${data.data.dt} </td>
            <td> ${data.data.notes} </td>
        </tr>
   `)
});

channel.bind('update-record_bd', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.gauge} </th>
        <td> ${data.data.matl} </td>
        <td> ${data.data.desc} </td>
        <td> ${data.data.thick} </td>
        <td> ${data.data.rad} </td>
        <td> ${data.data.bd} </td>
        <td> ${data.data.pt} </td>
        <td> ${data.data.dt} </td>
        <td> ${data.data.notes} </td>
    `)
 });





channel.bind('update-record_ship', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.job} </th>
        <td> ${data.data.date} </td>
        <td> ${data.data.track} </td>
        <td> ${data.data.delv} </td>
    `)
 });




// channel.bind('new-record_tl', (data) => {
//    $('#tjobs').append(`
//         <tr id="${data.data.id}">
//             <th scope="row"> ${data.data.job} </th>
//             <td> ${data.data.mtl} </td>
//             <td> ${data.data.mtln} </td>
//             <td> ${data.data.pgm} </td>
//             <td> ${data.data.pgmn} </td>
//             <td> ${data.data.tlh} </td>
//             <td> ${data.data.tlhn} </td>
//         </tr>
//    `)
// });

// TUBE LASER NOTES
channel.bind('update-record_pn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// SAW NOTES
channel.bind('update-record_sawn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// SHEAR NOTES
channel.bind('update-record_shearn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// FORMING NOTES
channel.bind('update-record_formingn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// PUNCH NOTES
channel.bind('update-record_punchn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// SLASER NOTES
channel.bind('update-record_slasern', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// FLASER NOTES
channel.bind('update-record_flasern', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// MACHINING NOTES
channel.bind('update-record_machiningn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// ENGINEERING NOTES
channel.bind('update-record_engn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// ENTERPRISE NOTES
channel.bind('update-record_entn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// SUPPLIES NOTES
channel.bind('update-record_supn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });



// PURCHASING NOTES
channel.bind('update-record_purchn', (data) => {
    $(`#${data.data.id}`).html(`
        <td> ${data.data.area} </td>
        <td> ${data.data.notes} </td>
    `)
 });


function multiplyBy()
{
    num1 = document.getElementById("first").value;
    num2 = document.getElementById("second").value;
    document.getElementById("result").innerHTML = num1 * num2;
}



$(document).ready(function () {
            $('#sidebarCollapse').on('click', function () {
                $('#sidebar').toggleClass('active');
            });
        });




// ENTERPRISE
channel.bind('new-record-ent', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
   $('#ent').append(`
        <tr id="${data.data.id}">
            <th scope="row"> ${data.data.name} </th>
            <td> ${data.data.need} </td>
            <td> ${data.data.needn} </td>
            <td> ${data.data.ordr} </td>
            <td> ${data.data.ordrn} </td>
            <td> ${data.data.verf} </td>
            <td> ${data.data.verfn} </td>
            <td> ${data.data.done} </td>
        </tr>
   `)
});

channel.bind('update-record-ent', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.name} </th>
        <td> ${data.data.need} </td>
        <td> ${data.data.needn} </td>
        <td> ${data.data.ordr} </td>
        <td> ${data.data.ordrn} </td>
        <td> ${data.data.verf} </td>
        <td> ${data.data.verfn} </td>
        <td> ${data.data.done} </td>
    `)
 });




// TODO LIST
channel.bind('new-record-todo', (data) => {
   $('#todo').append(`
        <tr id="${data.data.id}">
            <th scope="row"> ${data.data.rtype} </th>
            <td> ${data.data.area} </td>
            <td> ${data.data.desc} </td>
            <td> ${data.data.name} </td>
            <td> ${data.data.done} </td>
        </tr>
   `)
});

channel.bind('update-record-todo', (data) => {
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.rtype} </th>
        <td> ${data.data.area} </td>
        <td> ${data.data.desc} </td>
        <td> ${data.data.name} </td>
        <td> ${data.data.done} </td>
    `)
 });




// MAINTENANCE TODO LIST
channel.bind('new-record-mtodo', (data) => {
   $('#mtodo').append(`
        <tr id="${data.data.id}">
            <th scope="row"> ${data.data.rtype} </th>
            <td> ${data.data.area} </td>
            <td> ${data.data.desc} </td>
            <td> ${data.data.name} </td>
            <td> ${data.data.done} </td>
        </tr>
   `)
});

channel.bind('update-record-mtodo', (data) => {
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.rtype} </th>
        <td> ${data.data.area} </td>
        <td> ${data.data.desc} </td>
        <td> ${data.data.name} </td>
        <td> ${data.data.done} </td>
    `)
 });





// SUPPLIES
channel.bind('new-record-supplies', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
   $('#supplies').append(`
        <tr id="${data.data.id}">
            <th scope="row"> ${data.data.dept} </th>
            <td> ${data.data.need} </td>
            <td> ${data.data.desc} </td>
            <td> ${data.data.ordr} </td>
            <td> ${data.data.ordrn} </td>
            <td> ${data.data.done} </td>
        </tr>
   `)
});

channel.bind('update-record-supplies', (data) => {
    // const duedate = moment(`${data.data.duedate}`, 'DD/MM/YYYY').format('YYYY-MM-DD')
    $(`#${data.data.id}`).html(`
        <th scope="row"> ${data.data.dept} </th>
        <td> ${data.data.need} </td>
        <td> ${data.data.desc} </td>
        <td> ${data.data.ordr} </td>
        <td> ${data.data.ordrn} </td>
        <td> ${data.data.done} </td>
    `)
 });
