document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".evtap-fav-form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      event.stopPropagation();

      const url = form.getAttribute("action");
      const csrfToken = form.querySelector("input[name=csrfmiddlewaretoken]").value;
      const button = form.querySelector(".evtap-fav-btn");

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Sevimlilər siyahısı yenilənmədi");
          }
          return response.json();
        })
        .then(function (data) {
          button.innerHTML = data.is_favorited ? "&#9829;" : "&#9825;";
        })
        .catch(function () {
          form.submit();
        });
    });
  });

  document.querySelectorAll(".evtap-card-gallery, .evtap-detail-gallery").forEach(function (gallery) {
    const raw = gallery.getAttribute("data-images");
    const detailUrl = gallery.getAttribute("data-detail-url");
    const images = raw ? raw.split("|").filter(Boolean) : [];
    const imgEl = gallery.querySelector(".evtap-gallery-current");
    const dots = gallery.querySelectorAll(".evtap-card-dot");
    let index = 0;

    function render() {
      if (imgEl) {
        imgEl.src = images[index];
      }
      dots.forEach(function (dot, i) {
        dot.classList.toggle("active", i === index);
      });
    }

    function go(delta) {
      if (images.length < 2) return;
      index = (index + delta + images.length) % images.length;
      render();
    }

    const prev = gallery.querySelector(".evtap-card-nav-prev");
    const next = gallery.querySelector(".evtap-card-nav-next");
    if (prev) {
      prev.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        go(-1);
      });
    }
    if (next) {
      next.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        go(1);
      });
    }

    gallery.addEventListener("click", function (event) {
      if (event.target.closest(".evtap-card-nav")) {
        return;
      }
      if (detailUrl) {
        window.location.href = detailUrl;
      }
    });
  });

  document.querySelectorAll(".evtap-image-slot").forEach(function (slot) {
    const input = slot.querySelector('input[type="file"]');
    const tool = slot.querySelector(".evtap-crop-tool");
    const viewport = slot.querySelector(".evtap-crop-viewport");
    const imgEl = slot.querySelector(".evtap-crop-img");
    const zoomInput = slot.querySelector(".evtap-crop-zoom");
    const cropBoxInput = slot.querySelector('input[name$="-crop_box"]');
    if (!input || !tool || !viewport || !imgEl || !zoomInput || !cropBoxInput) {
      return;
    }

    let naturalW = 0;
    let naturalH = 0;
    let baseScale = 1;
    let scale = 1;
    let offsetX = 0;
    let offsetY = 0;
    let dragging = false;
    let startX = 0;
    let startY = 0;
    let startOffsetX = 0;
    let startOffsetY = 0;

    function clampOffsets() {
      const vw = viewport.clientWidth;
      const vh = viewport.clientHeight;
      const iw = naturalW * scale;
      const ih = naturalH * scale;
      const minX = Math.min(0, vw - iw);
      const minY = Math.min(0, vh - ih);
      offsetX = Math.max(minX, Math.min(0, offsetX));
      offsetY = Math.max(minY, Math.min(0, offsetY));
    }

    function updateCropBox() {
      const vw = viewport.clientWidth;
      const vh = viewport.clientHeight;
      const iw = naturalW * scale;
      const ih = naturalH * scale;
      if (!iw || !ih) {
        return;
      }
      cropBoxInput.value = JSON.stringify({
        x: -offsetX / iw,
        y: -offsetY / ih,
        width: vw / iw,
        height: vh / ih,
      });
    }

    function render() {
      imgEl.style.width = naturalW * scale + "px";
      imgEl.style.height = naturalH * scale + "px";
      imgEl.style.transform = "translate(" + offsetX + "px, " + offsetY + "px)";
      updateCropBox();
    }

    function startDrag(clientX, clientY) {
      dragging = true;
      startX = clientX;
      startY = clientY;
      startOffsetX = offsetX;
      startOffsetY = offsetY;
    }

    function moveDrag(clientX, clientY) {
      if (!dragging) {
        return;
      }
      offsetX = startOffsetX + (clientX - startX);
      offsetY = startOffsetY + (clientY - startY);
      clampOffsets();
      render();
    }

    function endDrag() {
      dragging = false;
    }

    input.addEventListener("change", function () {
      const file = input.files && input.files[0];
      if (!file) {
        tool.style.display = "none";
        cropBoxInput.value = "";
        return;
      }
      const reader = new FileReader();
      reader.onload = function (loadEvent) {
        imgEl.onload = function () {
          tool.style.display = "block";
          naturalW = imgEl.naturalWidth;
          naturalH = imgEl.naturalHeight;
          const vw = viewport.clientWidth;
          const vh = viewport.clientHeight;
          baseScale = Math.max(vw / naturalW, vh / naturalH);
          scale = baseScale;
          zoomInput.value = "100";
          offsetX = (vw - naturalW * scale) / 2;
          offsetY = (vh - naturalH * scale) / 2;
          clampOffsets();
          render();
        };
        imgEl.src = loadEvent.target.result;
      };
      reader.readAsDataURL(file);
    });

    zoomInput.addEventListener("input", function () {
      const zoomPct = parseFloat(zoomInput.value) || 100;
      scale = baseScale * (zoomPct / 100);
      clampOffsets();
      render();
    });

    viewport.addEventListener("mousedown", function (event) {
      event.preventDefault();
      startDrag(event.clientX, event.clientY);
    });
    window.addEventListener("mousemove", function (event) {
      moveDrag(event.clientX, event.clientY);
    });
    window.addEventListener("mouseup", endDrag);

    viewport.addEventListener(
      "touchstart",
      function (event) {
        const touch = event.touches[0];
        startDrag(touch.clientX, touch.clientY);
      },
      { passive: true }
    );
    viewport.addEventListener(
      "touchmove",
      function (event) {
        const touch = event.touches[0];
        moveDrag(touch.clientX, touch.clientY);
      },
      { passive: true }
    );
    viewport.addEventListener("touchend", endDrag);
  });
});
