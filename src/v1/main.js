import { createApp } from "vue";
import "../shared/variant-nav.css";
import { configureRuntime } from "../shared/runtime.js";
import { mountVariantNav } from "../shared/variant-nav.js";
import "./styles.css";
import App from "./legacy-app.js";

configureRuntime();
createApp(App).mount("#app");
mountVariantNav("v1");
