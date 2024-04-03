from flask import Flask, render_template_string
import psycopg2

def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host="ec2-3-224-58-73.compute-1.amazonaws.com",
            database="de84slt1iucctv",
            user="adaptativa_read",
            password="pe71d6441e182e2458c5fd7701d60d1d0023f68f74dbd0ea0f8e1211d05a14374",
            port="5432"
        )
    except Exception as e:
        print(f"Falha na conexão ao banco de dados: {e}")
    return conn

def execute_query():
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("""
               select 
                i.name as curso,
                ic2.name as escola,
                q.name as simulado,
                count( users.id) as n_user_id
                from quiz_user_progresses qup  
                inner join users on users.id =qup.user_id 
                inner join quizzes q on q.id = qup.quiz_id 
                inner join institution_enrollments ie on ie.user_id = qup.user_id 
                inner join institution_classrooms ic on ic.id =ie.classroom_id  
                inner join institution_levels il on il.id = ic.level_id 
                inner join institution_courses ic3 on ic3.id = il.course_id 
                inner join institution_colleges ic2 on ic2.id =  ic3.institution_college_id  and ic2.id = ie.college_id 
                inner join institutions i on i.id = ic2.institution_id  
                inner join regions r on ic2.region_id =r.id 
                inner join cities c on c.id =r.city_id 
                where qup.finished = true and qup.quiz_id in (
                select iq.quiz_id  from institutions_quizzes iq where iq.institution_id in (244,280,321,246,284,322,324,245,287,323,325,326,247,283,285,286,327,330,331)
                )
                and ie.institution_id in (244,280,321,246,284,322,324,245,287,323,325,326,247,283,285,286,327,330,331)
                and ic2.year = 2024
                and c.id = 2313302 -- tauá - ce
                group by curso, escola, simulado 
                order by curso, escola, simulado;
                """)
                column_names = [desc[0] for desc in cur.description]
                results = cur.fetchall()
                return (column_names, results)
        except Exception as e:
            print(f"Falha na execução da consulta: {e}")
        finally:
            conn.close()
    return ([], [])  # Retorna listas vazias se a conexão falhar ou ocorrer uma exceção

app = Flask(__name__)

@app.route('/')
def index():
    column_names, query_results = execute_query()
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resultados da Consulta</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                background-color: #f5f5f5;
            }
            .header-container {
                text-align: center;
                margin: 20px;
            }
            .table-container {
                width: 80%;
                max-width: 1000px;
                box-shadow: 0 2px 3px rgba(0,0,0,0.1);
                background-color: #fff;
                margin: 20px 0;
            }
            table {
                border-collapse: collapse;
                width: 1000px;
            }
            th, td {
                text-align: center;
                padding: 10px;
                font-size: 16px;
                width: 25px

            }
            th {
                background-color:green;
                color: white;
            }
            tr:nth-child(even) {background-color: #f2f2f2;}
        </style>
    </head>
    <body>
               <table>
            <thead>
                <tr>
                    {% for col_name in column_names %}
                    <th>{{ col_name }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in query_results %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, column_names=column_names, query_results=query_results)

if __name__ == "__main__":
    app.run(debug=True)






