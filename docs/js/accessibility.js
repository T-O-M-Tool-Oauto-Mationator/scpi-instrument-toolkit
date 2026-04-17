/**
 * WCAG 2.1 AA accessibility fixes for MkDocs Material theme.
 * Adds ARIA attributes that the theme omits by default.
 */
document.addEventListener("DOMContentLoaded", function () {
  /* 1. SVG icon buttons: add aria-label to icon-only controls (WCAG 1.1.1) */
  var iconLabels = {
    __drawer: "Open navigation menu",
    __search: "Open search",
  };
  document.querySelectorAll("label.md-header__button").forEach(function (el) {
    var target = el.getAttribute("for");
    if (target && iconLabels[target] && !el.getAttribute("aria-label")) {
      el.setAttribute("aria-label", iconLabels[target]);
    }
  });

  /* Theme toggle buttons */
  document
    .querySelectorAll('form[data-md-component="palette"] label')
    .forEach(function (el) {
      if (!el.getAttribute("aria-label")) {
        var title = el.querySelector("svg title");
        var name =
          el.getAttribute("title") ||
          (title ? title.textContent : "Toggle color scheme");
        el.setAttribute("aria-label", name);
      }
    });

  /* 2. Tabbed content: add ARIA tab roles (WCAG 1.3.1, 4.1.2) */
  document.querySelectorAll(".tabbed-set").forEach(function (tabSet) {
    var labelContainer = tabSet.querySelector(".tabbed-labels");
    if (!labelContainer) return;

    labelContainer.setAttribute("role", "tablist");

    labelContainer.querySelectorAll("label").forEach(function (label) {
      label.setAttribute("role", "tab");

      var inputId = label.getAttribute("for");
      if (inputId) {
        var input = document.getElementById(inputId);
        var isSelected = input && input.checked;
        label.setAttribute("aria-selected", isSelected ? "true" : "false");
      }
    });

    var panels = tabSet.querySelectorAll(".tabbed-block");
    panels.forEach(function (panel, i) {
      panel.setAttribute("role", "tabpanel");
      var labels = labelContainer.querySelectorAll("label");
      if (labels[i]) {
        var panelId = "tabpanel-" + Math.random().toString(36).substr(2, 6);
        panel.setAttribute("id", panelId);
        labels[i].setAttribute("aria-controls", panelId);
      }
    });

    /* Update aria-selected when tabs change */
    tabSet.querySelectorAll('input[type="radio"]').forEach(function (input) {
      input.addEventListener("change", function () {
        labelContainer.querySelectorAll("label").forEach(function (l) {
          var lid = l.getAttribute("for");
          var li = document.getElementById(lid);
          l.setAttribute("aria-selected", li && li.checked ? "true" : "false");
        });
      });
    });
  });

  /* 3. Nav toggle labels: add aria-expanded (WCAG 4.1.2) */
  document.querySelectorAll(".md-nav__toggle").forEach(function (toggle) {
    var label = document.querySelector('label[for="' + toggle.id + '"]');
    if (label) {
      label.setAttribute("aria-expanded", toggle.checked ? "true" : "false");
      toggle.addEventListener("change", function () {
        label.setAttribute("aria-expanded", toggle.checked ? "true" : "false");
      });
    }
  });

  /* 4. Decorative SVGs: mark as presentation (WCAG 1.1.1) */
  document.querySelectorAll("svg").forEach(function (svg) {
    /* Skip SVGs that already have accessible names */
    if (svg.getAttribute("aria-label") || svg.querySelector("title")) return;

    var parent = svg.parentElement;
    /* If parent has aria-label, the SVG is decorative */
    if (parent && parent.getAttribute("aria-label")) {
      svg.setAttribute("aria-hidden", "true");
      svg.setAttribute("focusable", "false");
      return;
    }

    /* Standalone decorative SVGs (icons inside labeled buttons) */
    if (
      parent &&
      (parent.tagName === "LABEL" ||
        parent.tagName === "BUTTON" ||
        parent.tagName === "A")
    ) {
      svg.setAttribute("aria-hidden", "true");
      svg.setAttribute("focusable", "false");
    }
  });
});
