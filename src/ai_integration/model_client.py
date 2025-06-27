import openai
import time
import json
from typing import Dict, List, Optional

class AIModelClient:
    def __init__(self, api_key: str = None, model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model_name = model_name
        if api_key:
            openai.api_key = api_key
    
    def generate_driver_code(self, prompt: str, max_tokens: int = 1500) -> Dict:
        """Generate Linux driver code using AI model"""
        try:
            system_prompt = """You are an expert Linux kernel developer. 
Generate clean, working Linux device driver code following kernel coding standards.
Include proper error handling, memory management, and module structure."""
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1  # Lower temperature for more consistent code
            )
            
            code = response.choices[0].message.content
            
            return {
                "success": True,
                "code": code,
                "model": self.model_name,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": None
            }
    
    def batch_generate(self, prompts: List[str], delay: float = 1.0) -> List[Dict]:
        """Generate code for multiple prompts with rate limiting"""
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"Generating code for prompt {i+1}/{len(prompts)}")
            
            result = self.generate_driver_code(prompt)
            results.append(result)
            
            if i < len(prompts) - 1:  # Don't delay after last prompt
                time.sleep(delay)
        
        return results

class MockAIClient:
    """Mock client for testing without API keys"""
    
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name
    
    def generate_driver_code(self, prompt: str, max_tokens: int = 1500) -> Dict:
        """Generate mock driver code for testing"""
        
        # Simple template based on prompt keywords
        if "character" in prompt.lower():
            code = self._get_char_driver_template()
        elif "platform" in prompt.lower():
            code = self._get_platform_driver_template()
        else:
            code = self._get_basic_driver_template()
        
        return {
            "success": True,
            "code": code,
            "model": self.model_name,
            "tokens_used": 500
        }
    
    def batch_generate(self, prompts: List[str], delay: float = 0.1) -> List[Dict]:
        """Generate mock code for multiple prompts"""
        results = []
        
        for prompt in prompts:
            result = self.generate_driver_code(prompt)
            results.append(result)
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
MODULE_AUTHOR("AI Generated");
MODULE_DESCRIPTION("Character device driver");'''
    
    def _get_platform_driver_template(self) -> str:
        return '''#include <linux/init.h>
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/io.h>
#include <linux/interrupt.h>

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
MODULE_AUTHOR("AI Generated");
MODULE_DESCRIPTION("Platform device driver");'''
    
    def _get_basic_driver_template(self) -> str:
        return '''#include <linux/init.h>
#include <linux/module.h>

static int __init basic_init(void)
{
    printk(KERN_INFO "Basic driver loaded\\n");
    return 0;
}

static void __exit basic_exit(void)
{
    printk(KERN_INFO "Basic driver unloaded\\n");
}

module_init(basic_init);
module_exit(basic_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("AI Generated");
MODULE_DESCRIPTION("Basic kernel module");'''
