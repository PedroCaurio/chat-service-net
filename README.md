# chat-service-net
Projeto para disciplina de Redes de Computadores com o objetivo de desenvolver um chat utilizando a biblioteca de sockets nativas do python, usando protocolos TCP e UDP

### Running

1. **Clone the repository**:

   ```bash
   git clone https://github.com/PedroCaurio/chat-service-net.git
   cd chat-service-net
   ```

2. **Copy environment variables**:

   ```bash
   cp .env.example .env
   ```
3. **Possible errors**:
   Caso dê algum erro de plugin do qt no linux, rodar esses comandos

   ```
   sudo apt update
   sudo apt install libxcb-cursor0
   ´´´

4. **Runing**:
   Para rodar é só ativar o venv com:
   ```
   source .venv/bin/activate
   ´´´
   Após isso, para o server:
   ```
   python server/server.py
   ´´´
   E para cada cliente:
   ```
   python client/main.py
   ´´´
### Setting up Local Environment

1. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Navigate to the project directory**:

   ```bash
   cd chat-service-net/
   ```

3. **Install dependencies**:

   ```bash
   uv sync
   ```


5. **Logins**:
   Logins disponíveis
   - user: pedro, password: 1234
   - user: alice, password: 1234
   - user: felipe, password: 1234