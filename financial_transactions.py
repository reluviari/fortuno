import datetime
import json
from collections import defaultdict

class FinancialTransaction:
    def __init__(self, date, description, category, amount, transaction_type):
        self.date = date
        self.description = description
        self.category = category
        self.amount = float(amount)
        self.transaction_type = transaction_type

class FinancialRecord:
    def __init__(self):
        self.transactions = []
        self.load_transactions()

    def add_transaction(self, date, description, category, amount, transaction_type):
        amount = float(amount)
        if transaction_type == "Despesa":
            amount = -abs(amount)
        else:
            amount = abs(amount)

        transaction = FinancialTransaction(date, description, category, amount, transaction_type)
        self.transactions.append(transaction)
        self.save_transactions()

    def list_transactions(self):
        return self.transactions

    def get_balance(self):
        return sum(t.amount for t in self.transactions)

    def save_transactions(self):
        with open('transactions.json', 'w') as f:
            json.dump([
                {
                    'date': t.date.strftime("%Y-%m-%d %H:%M:%S"),
                    'description': t.description,
                    'category': t.category,
                    'amount': t.amount,
                    'transaction_type': t.transaction_type
                } for t in self.transactions
            ], f, default=str)

    def load_transactions(self):
        try:
            with open('transactions.json', 'r') as f:
                data = json.load(f)
                self.transactions = []
                for t in data:
                    date = self.parse_date(t['date'])
                    self.transactions.append(FinancialTransaction(
                        date,
                        t['description'],
                        t['category'],
                        t['amount'],
                        t['transaction_type']
                    ))
        except FileNotFoundError:
            self.transactions = []

    def parse_date(self, date_string):
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M:%S"
        ]
        for date_format in date_formats:
            try:
                return datetime.datetime.strptime(date_string, date_format)
            except ValueError:
                continue
        raise ValueError(f"Data não reconhecida: {date_string}")

    def report_by_category(self):
        if not self.transactions:
            return "Nenhuma transação registrada."

        expenses_by_category = defaultdict(float)
        income_by_category = defaultdict(float)

        for t in self.transactions:
            if t.transaction_type == "Despesa":
                expenses_by_category[t.category] += abs(t.amount)
            else:
                income_by_category[t.category] += t.amount

        total_expenses = sum(expenses_by_category.values())
        total_income = sum(income_by_category.values())

        return {
            "Despesas": dict(expenses_by_category),
            "Receitas": dict(income_by_category),
            "Total de Despesas": total_expenses,
            "Total de Receitas": total_income,
            "Saldo": total_income - total_expenses
        }

def main():
    record = FinancialRecord()

    while True:
        print("\n1. Adicionar despesa")
        print("2. Adicionar receita")
        print("3. Listar transações")
        print("4. Mostrar saldo")
        print("5. Relatório por categoria")
        print("6. Sair")

        choice = input("Escolha uma opção: ")

        if choice in ["1", "2"]:
            date = input("Data da transação (DD/MM/AAAA): ")
            date = datetime.datetime.strptime(date, "%d/%m/%Y")
            description = input("Descrição da transação: ")
            category = input("Categoria da transação: ")
            amount = float(input("Valor da transação: "))
            transaction_type = "Despesa" if choice == "1" else "Receita"
            record.add_transaction(date, description, category, amount, transaction_type)
        elif choice == "3":
            transactions = record.list_transactions()
            for t in transactions:
                print(f"{t.date.strftime('%d/%m/%Y')}, {t.description}, {t.category}, R$ {abs(t.amount):.2f}, {t.transaction_type}")
        elif choice == "4":
            balance = record.get_balance()
            print(f"Saldo atual: R$ {balance:.2f}")
        elif choice == "5":
            report = record.report_by_category()
            if isinstance(report, str):
                print(report)
            else:
                print("\nRelatório por Categoria:")
                print("\nDespesas:")
                for category, amount in report["Despesas"].items():
                    print(f"{category}: R$ {amount:.2f}")
                print(f"\nTotal de Despesas: R$ {report['Total de Despesas']:.2f}")

                print("\nReceitas:")
                for category, amount in report["Receitas"].items():
                    print(f"{category}: R$ {amount:.2f}")
                print(f"\nTotal de Receitas: R$ {report['Total de Receitas']:.2f}")

                print(f"\nSaldo: R$ {report['Saldo']:.2f}")
        elif choice == "6":
            print("Saindo do programa. Até logo!")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()