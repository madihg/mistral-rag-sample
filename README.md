# RAG Chatbot with Mistral AI

A Retrieval-Augmented Generation (RAG) chatbot built with Flask and Mistral AI.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Mistral API key:
   ```
   MISTRAL_API_KEY=your_api_key_here
   ```
5. Add your text file as `essay.txt` in the project root

## Local Development

Run the Flask application:
```bash
python app.py
```

The application will be available at `http://localhost:5001`

## Deployment to Vercel

1. Push your code to GitHub
2. Connect your GitHub repository to Vercel
3. Add your environment variables in the Vercel dashboard:
   - `MISTRAL_API_KEY`: Your Mistral API key
4. Deploy!

## Environment Variables

- `MISTRAL_API_KEY`: Your Mistral AI API key (required)

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS)
- `essay.txt`: Source text for the RAG system
- `requirements.txt`: Python dependencies
- `vercel.json`: Vercel deployment configuration 