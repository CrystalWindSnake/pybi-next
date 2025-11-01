import type { Ref } from "vue";

declare module "instaui" {
  export function useBindingGetter(): {
    getValue: (key: any) => any;
    getRef: (key: any) => Ref<any>;
  };

  export function useLanguage(): Ref<string>;
}
