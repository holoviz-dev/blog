
// Ugly hack - see #2574 for more information
if (!(document.getElementById('983aedf5-7c1c-4e78-863a-763746f0abcd')) && !(document.getElementById('_anim_imgNone'))) {
  console.log("Creating DOM nodes dynamically for assumed nbconvert export. To generate clean HTML output set HV_DOC_HTML as an environment variable.")
  var htmlObject = document.createElement('div');
  htmlObject.innerHTML = `<div id='983aedf5-7c1c-4e78-863a-763746f0abcd' style='display: table; margin: 0 auto;'>
    <div id="fig_983aedf5-7c1c-4e78-863a-763746f0abcd">
      
<div class="bk-root">
    <div class="bk-plotdiv" id="02252e01-de93-4591-a0d6-56383bc62944"></div>
</div>
    </div>
    </div>`;
  var scriptTags = document.getElementsByTagName('script');
  var parentTag = scriptTags[scriptTags.length-1].parentNode;
  parentTag.append(htmlObject)
}
(function(root) {
  function embed_document(root) {
    
  var render_items = [{"docid":"9a9b96d6-dfe9-46fa-a6ef-628ad0f3f3c4","elementid":"02252e01-de93-4591-a0d6-56383bc62944","modelid":"983aedf5-7c1c-4e78-863a-763746f0abcd","notebook_comms_target":"1fdf3785026a4c4e824608d7a7cdecc2"}];
  root.Bokeh.embed.embed_items_notebook(docs_json, render_items);

  }
  if (root.Bokeh !== undefined) {
    embed_document(root);
  } else {
    var attempts = 0;
    var timer = setInterval(function(root) {
      if (root.Bokeh !== undefined) {
        embed_document(root);
        clearInterval(timer);
      }
      attempts++;
      if (attempts > 100) {
        console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing")
        clearInterval(timer);
      }
    }, 10, root)
  }
})(window);

    function msg_handler(msg) {
      var buffers = msg.buffers;
      var msg = msg.content.data;
      
var plot_id = "983aedf5-7c1c-4e78-863a-763746f0abcd";
if (plot_id in HoloViews.plot_index) {
  var plot = HoloViews.plot_index[plot_id];
} else {
  var plot = Bokeh.index[plot_id];
}

if (plot_id in HoloViews.receivers) {
  var receiver = HoloViews.receivers[plot_id];
} else if (Bokeh.protocol === undefined) {
  return;
} else {
  var receiver = new Bokeh.protocol.Receiver();
  HoloViews.receivers[plot_id] = receiver;
}

if (buffers.length > 0) {
  receiver.consume(buffers[0].buffer)
} else {
  receiver.consume(msg)
}

const comm_msg = receiver.message;
if (comm_msg != null) {
  plot.model.document.apply_json_patch(comm_msg.content, comm_msg.buffers)
}

    }
    HoloViews.comm_manager.register_target('983aedf5-7c1c-4e78-863a-763746f0abcd', '1fdf3785026a4c4e824608d7a7cdecc2', msg_handler);
    