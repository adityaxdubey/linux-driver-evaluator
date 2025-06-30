import time
import json
import requests
from typing import Dict, List, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class MultiModelClient:
    def __init__(self, model_type: str = "mock", api_key: str = None):
        self.model_type = model_type.lower()
        self.api_key = api_key
        
        if self.model_type == "openai" and OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key
        elif self.model_type == "gemini" and GEMINI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
        
    def generate_driver_code(self, prompt: str, max_tokens: int = 2048) -> Dict:
        """generate driver code using selected model"""
        
        if self.model_type == "openai":
            return self._generate_openai(prompt, max_tokens)
        elif self.model_type == "gemini":
            return self._generate_gemini(prompt, max_tokens)
        else:
            return self._generate_mock(prompt)
    
    def _generate_openai(self, prompt: str, max_tokens: int) -> Dict:
        """generate code using openai"""
        if not OPENAI_AVAILABLE or not self.api_key:
            return {"success": False, "error": "openai not available or no api key"}
        
        try:
            system_prompt = """you are an expert linux kernel developer. 
generate clean, working linux device driver code following kernel coding standards.
include proper error handling, memory management, and module structure."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1
            )
            
            code = response.choices[0].message.content
            
            return {
                "success": True,
                "code": code,
                "model": "gpt-3.5-turbo",
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "code": None}
    
    def _generate_gemini(self, prompt: str, max_tokens: int) -> Dict:
        """generate code using google gemini with multiple model fallbacks"""
        if not GEMINI_AVAILABLE or not self.api_key:
            return {"success": False, "error": "gemini not available or no api key"}
        
        # updated model list as requested
        model_names = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-pro",
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-pro"
        ]
        
        # define safety settings to be less restrictive
        safety_settings = {
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        }
        
        full_prompt = f"""you are an expert linux kernel developer. 
generate clean, working linux device driver code following kernel coding standards.
include proper error handling, memory management, and module structure.

user request: {prompt}

provide only the c code without explanations."""

        for model_name in model_names:
            try:
                print(f"trying gemini model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.1,
                    ),
                    safety_settings=safety_settings  # pass safety settings here
                )
                
                # more robust check for content before accessing response.text
                if response.parts:
                    return {
                        "success": True,
                        "code": response.text,
                        "model": model_name,
                        "tokens_used": len(response.text.split())
                    }
                else:
                    # this handles the case where the response was blocked
                    finish_reason = response.candidates[0].finish_reason if response.candidates else "unknown"
                    print(f"model {model_name} returned empty response. finish_reason: {finish_reason}")
                    
            except Exception as e:
                print(f"model {model_name} failed: {str(e)}")
                continue
        
        # if all models fail
        return {"success": False, "error": "all gemini models failed or returned no content"}
    
    def _generate_mock(self, prompt: str) -> Dict:
        """generate mock driver code for testing"""
        
        if "character" in prompt.lower():
            code = self._get_char_driver_template()
        elif "platform" in prompt.lower():
            code = self._get_platform_driver_template()
        else:
            code = self._get_basic_driver_template()
        
        return {
            "success": True,
            "code": code,
            "model": "mock-generator",
            "tokens_used": 500
        }
    
    def batch_generate(self, prompts: List[str], delay: float = 1.0) -> List[Dict]:
        """generate code for multiple prompts"""
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"generating code for prompt {i+1}/{len(prompts)}")
            
            result = self.generate_driver_code(prompt)
            results.append(result)
            
            if i < len(prompts) - 1 and self.model_type != "mock":
                time.sleep(delay)
        
        return results
    
    def _get_char_driver_template(self) -> str:
        return '''#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

#define DEVICE_NAME "chardev"
#define BUFFER_SIZE 1024

static int major_number;
static char device_buffer[BUFFER_SIZE];

static int device_open(struct inode *inode, struct file *file)
{
    return 0;
}

static int device_release(struct inode *inode, struct file *file)
{
    return 0;
}

static ssize_t device_read(struct file *file, char __user *user_buffer, 
                          size_t size, loff_t *offset)
{
    if (copy_to_user(user_buffer, device_buffer, size)) {
        return -EFAULT;
    }
    return size;
}

static ssize_t device_write(struct file *file, const char __user *user_buffer,
                           size_t size, loff_t *offset)
{
    if (size > BUFFER_SIZE) {
        return -EINVAL;
    }
    
    if (copy_from_user(device_buffer, user_buffer, size)) {
        return -EFAULT;
    }
    return size;
}

static struct file_operations fops = {
    .open = device_open,
    .release = device_release,
    .read = device_read,
    .write = device_write,
};

static int __init driver_init(void)
{
    major_number = register_chrdev(0, DEVICE_NAME, &fops);
    if (major_number < 0) {
        return major_number;
    }
    return 0;
}

static void __exit driver_exit(void)
{
    unregister_chrdev(major_number, DEVICE_NAME);
}

module_init(driver_init);
module_exit(driver_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("ai generated");
MODULE_DESCRIPTION("character device driver");'''
    
    def _get_platform_driver_template(self) -> str:
        return '''#include <linux/init.h>
#include <linux/module.h>
#include <linux/platform_device.h>

#define DRIVER_NAME "platform_driver"

static int platform_probe(struct platform_device *pdev)
{
    return 0;
}

static int platform_remove(struct platform_device *pdev)
{
    return 0;
}

static struct platform_driver my_platform_driver = {
    .probe = platform_probe,
    .remove = platform_remove,
    .driver = {
        .name = DRIVER_NAME,
    },
};

static int __init driver_init(void)
{
    return platform_driver_register(&my_platform_driver);
}

static void __exit driver_exit(void)
{
    platform_driver_unregister(&my_platform_driver);
}

module_init(driver_init);
module_exit(driver_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("ai generated");
MODULE_DESCRIPTION("platform device driver");'''
    
    def _get_basic_driver_template(self) -> str:
        return '''#include <linux/init.h>
#include <linux/module.h>

static int __init basic_init(void)
{
    printk(KERN_INFO "basic driver loaded\\n");
    return 0;
}

static void __exit basic_exit(void)
{
    printk(KERN_INFO "basic driver unloaded\\n");
}

module_init(basic_init);
module_exit(basic_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("ai generated");
MODULE_DESCRIPTION("basic kernel module");'''
