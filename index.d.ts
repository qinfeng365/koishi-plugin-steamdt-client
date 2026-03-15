import { Context, Schema } from 'koishi';
export declare const name = "steamdt-client";
export declare const usage = "\nSteamDT \u5F02\u52A8\u6570\u636E\u722C\u866B\u5BA2\u6237\u7AEF\n\n\u652F\u6301\u7684\u6307\u4EE4\uFF1A\n- /scrape [scrolls] [priority] - \u6DFB\u52A0\u722C\u53D6\u4EFB\u52A1\n- /queue - \u67E5\u770B\u961F\u5217\u72B6\u6001\n- /task [task_id] - \u67E5\u770B\u4EFB\u52A1\u7ED3\u679C\n- /image [task_id] - \u83B7\u53D6\u4EFB\u52A1\u56FE\u7247\n- /health - \u5065\u5EB7\u68C0\u67E5\n- /steamdt test - \u6D4B\u8BD5API\u8FDE\u63A5\n";
export interface Config {
    apiUrl: string;
    timeout: number;
    retryAttempts: number;
    retryDelay: number;
    enableDetailedLogging: boolean;
}
export declare const Config: Schema<Config>;
export declare function apply(ctx: Context, config: Config): void;
//# sourceMappingURL=koishi_client.d.ts.map