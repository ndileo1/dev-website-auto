import os
import shutil
import argparse

def generate_hugo_site(client_name, template_dir="hugo-template", output_base_dir="sites"):
    """
    Generates a new Hugo site based on a template for a specific client.
    """
    if not os.path.exists(template_dir):
        print(f"Error: Template directory '{template_dir}' does not exist.")
        return

    # Create safe directory name from client name
    client_dir_name = "".join([c if c.isalnum() else "_" for c in client_name]).lower()
    output_dir = os.path.join(output_base_dir, client_dir_name)

    if os.path.exists(output_dir):
        print(f"Warning: Directory '{output_dir}' already exists. Overwriting...")
        shutil.rmtree(output_dir)

    # 1. Copy the template to the new destination
    print(f"Copying template from {template_dir} to {output_dir}...")
    shutil.copytree(template_dir, output_dir, dirs_exist_ok=True)

    # 2. Update config file (hugo.toml)
    config_path = os.path.join(output_dir, "hugo.toml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_content = f.read()
        
        # Simple replacement of title (assuming title exists in the default hugo config)
        if "title =" in config_content:
            # Replace the title line
            lines = config_content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("title ="):
                    new_lines.append(f"title = '{client_name}'")
                else:
                    new_lines.append(line)
            config_content = '\n'.join(new_lines)
        else:
            config_content += f"\ntitle = '{client_name}'\n"

        with open(config_path, "w") as f:
            f.write(config_content)
        
        print(f"Updated {config_path} with title: {client_name}")

    # 3. Add homepage content
    content_dir = os.path.join(output_dir, "content")
    os.makedirs(content_dir, exist_ok=True)
    index_path = os.path.join(content_dir, "_index.md")
    
    with open(index_path, "w") as f:
        f.write(f"""---
title: "Accueil"
date: 2026-01-01
draft: false
---

# Bienvenue chez {client_name}

Nous sommes ravis de vous accueillir. Ce site est actuellement en construction.
""")

    print(f"Created homepage content in {index_path}")
    print(f"Site successfully generated in '{output_dir}'.")
    print(f"To preview the site, run: cd {output_dir} && hugo server -D")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Hugo website for a client.")
    parser.add_argument("client_name", help="Name of the client/business")
    args = parser.parse_args()

    generate_hugo_site(args.client_name)
