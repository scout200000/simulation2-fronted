import { createRouter, createWebHashHistory } from "vue-router";
import PortalView from "../views/PortalView.vue";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: "/",
      name: "portal",
      component: PortalView
    },
    {
      path: "/v1",
      name: "v1",
      component: () => import("../views/V1View.vue")
    },
    {
      path: "/v2",
      name: "v2",
      component: () => import("../views/V2View.vue")
    },
    {
      path: "/:pathMatch(.*)*",
      redirect: "/"
    }
  ]
});

export default router;
