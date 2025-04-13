import * as vscode from 'vscode';
import * as fs from 'fs';
import axios from 'axios';
import * as path from 'path';
import * as dotenv from 'dotenv';

dotenv.config();

const HF_API_TOKEN = process.env.HF_API_TOKEN;
const API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder";

export function activate(context: vscode.ExtensionContext) {
  let disposable = vscode.commands.registerCommand('ai-task-runner.runTask', async () => {
    const task = await vscode.window.showInputBox({ prompt: "Enter your task" });
    if (!task) return;

    const loading = vscode.window.setStatusBarMessage("⏳ Asking AI...");
    try {
      const response = await axios.post(API_URL, {
        inputs: task,
        parameters: {
          max_new_tokens: 200,
          temperature: 0.2
        }
      }, {
        headers: {
          Authorization: `Bearer ${HF_API_TOKEN}`,
          "Content-Type": "application/json"
        }
      });

      const result = response.data[0]?.generated_text || 'No response';
      const filePath = path.join(vscode.workspace.rootPath || context.extensionPath, 'generated_script.py');
      fs.writeFileSync(filePath, result);

      vscode.window.showInformationMessage(`✅ Code generated and saved to ${filePath}`);
    } catch (err: any) {
      vscode.window.showErrorMessage(`❌ Failed: ${err.message}`);
    } finally {
      loading.dispose();
    }
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
