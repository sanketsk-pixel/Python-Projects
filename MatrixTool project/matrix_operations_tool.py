
import numpy as np
import os
import sys

# Make NumPy's own printing cleaner if it's ever used directly
np.set_printoptions(precision=4, suppress=True)


class MatrixOperationsTool:
    def __init__(self):
        # Stores all matrices created in this session: {"A": np.array(...), ...}
        self.matrices = {}

    
    # Display helpers

    def print_header(self, title):
        width = 64
        print("\n" + "=" * width)
        print(title.center(width))
        print("=" * width)

    def format_matrix(self, matrix):
        """Return a neatly boxed, aligned string representation of a matrix."""
        matrix = np.atleast_2d(matrix)
        rows, cols = matrix.shape

        def fmt(val):
            if np.iscomplexobj(matrix):
                return f"{val:.3g}"
            if float(val).is_integer():
                return str(int(val))
            return f"{val:.4g}"

        str_vals = [[fmt(matrix[r, c]) for c in range(cols)] for r in range(rows)]
        col_widths = [max(len(str_vals[r][c]) for r in range(rows)) for c in range(cols)]

        inner_width = sum(col_widths) + 2 * (cols - 1) + 2
        top = "┌" + " " * inner_width + "┐"
        bottom = "└" + " " * inner_width + "┘"

        lines = [top]
        for r in range(rows):
            row_str = "  ".join(str_vals[r][c].rjust(col_widths[c]) for c in range(cols))
            lines.append("│ " + row_str + " │")
        lines.append(bottom)
        return "\n".join(lines)

    def print_matrix(self, name, matrix):
        print(f"\nMatrix '{name}'  (shape: {matrix.shape[0]} x {matrix.shape[1]})")
        print(self.format_matrix(matrix))

 
    # Input helpers
    
    def get_matrix_name(self, prompt="Enter a name for the matrix: "):
        return input(prompt).strip().upper()

    def input_dimensions(self):
        while True:
            try:
                rows = int(input("Number of rows: "))
                cols = int(input("Number of columns: "))
                if rows <= 0 or cols <= 0:
                    print("Rows and columns must be positive integers.")
                    continue
                return rows, cols
            except ValueError:
                print("Please enter valid whole numbers.")

    def select_matrix(self, prompt="Enter matrix name: "):
        if not self.matrices:
            print("No matrices available yet. Please create one first (Menu option 1).")
            return None
        print("Available matrices:", ", ".join(self.matrices.keys()))
        name = input(prompt).strip().upper()
        if name not in self.matrices:
            print(f"Matrix '{name}' not found.")
            return None
        return name

    def maybe_save_result(self, result):
        save = input("\nSave this result as a new matrix? (y/n): ").strip().lower()
        if save == "y":
            name = self.get_matrix_name("Enter a name for the result: ")
            self.matrices[name] = np.array(result, dtype=float) if not np.iscomplexobj(result) else result
            print(f"Saved as '{name}'.")

   
    # Matrix creation

    def create_matrix(self):
        self.print_header("CREATE A NEW MATRIX")
        name = self.get_matrix_name("Enter a name for the matrix (e.g. A, B, M1): ")
        if name in self.matrices:
            overwrite = input(f"Matrix '{name}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != "y":
                print("Cancelled.")
                return

        print("\nHow do you want to fill the matrix?")
        print("  1. Enter values manually")
        print("  2. Fill with random integers")
        print("  3. Identity matrix")
        print("  4. Zeros matrix")
        print("  5. Ones matrix")
        choice = input("Choose an option (1-5): ").strip()

        rows, cols = self.input_dimensions()

        if choice == "1":
            print(f"\nEnter each row as {cols} numbers separated by spaces.")
            data = []
            for i in range(rows):
                while True:
                    raw = input(f"Row {i + 1}: ").strip().split()
                    if len(raw) != cols:
                        print(f"Expected {cols} values, got {len(raw)}. Try again.")
                        continue
                    try:
                        data.append([float(x) for x in raw])
                        break
                    except ValueError:
                        print("Please enter valid numbers only.")
            matrix = np.array(data)

        elif choice == "2":
            try:
                low = int(input("Minimum value (e.g. -10): "))
                high = int(input("Maximum value (e.g. 10): "))
            except ValueError:
                print("Invalid numbers, defaulting to range -10 to 10.")
                low, high = -10, 10
            matrix = np.random.randint(low, high + 1, size=(rows, cols)).astype(float)

        elif choice == "3":
            matrix = np.eye(rows, cols)
        elif choice == "4":
            matrix = np.zeros((rows, cols))
        elif choice == "5":
            matrix = np.ones((rows, cols))
        else:
            print("Invalid choice, defaulting to a zeros matrix.")
            matrix = np.zeros((rows, cols))

        self.matrices[name] = matrix
        print(f"\nMatrix '{name}' created successfully!")
        self.print_matrix(name, matrix)

    def display_all(self):
        self.print_header("ALL STORED MATRICES")
        if not self.matrices:
            print("No matrices stored yet. Use option 1 to create one.")
            return
        for name, m in self.matrices.items():
            self.print_matrix(name, m)

    def delete_matrix(self):
        self.print_header("DELETE A MATRIX")
        name = self.select_matrix("Matrix name to delete: ")
        if name is None:
            return
        del self.matrices[name]
        print(f"Matrix '{name}' deleted.")

    
    # Core operations
   
    def operation_add(self):
        self.print_header("MATRIX ADDITION (A + B)")
        a = self.select_matrix("First matrix name: ")
        if a is None:
            return
        b = self.select_matrix("Second matrix name: ")
        if b is None:
            return
        A, B = self.matrices[a], self.matrices[b]
        if A.shape != B.shape:
            print(f"Error: shapes {A.shape} and {B.shape} do not match. Addition needs identical shapes.")
            return
        result = A + B
        print(f"\nResult of '{a}' + '{b}':")
        print(self.format_matrix(result))
        self.maybe_save_result(result)

    def operation_subtract(self):
        self.print_header("MATRIX SUBTRACTION (A - B)")
        a = self.select_matrix("First matrix name: ")
        if a is None:
            return
        b = self.select_matrix("Second matrix name: ")
        if b is None:
            return
        A, B = self.matrices[a], self.matrices[b]
        if A.shape != B.shape:
            print(f"Error: shapes {A.shape} and {B.shape} do not match. Subtraction needs identical shapes.")
            return
        result = A - B
        print(f"\nResult of '{a}' - '{b}':")
        print(self.format_matrix(result))
        self.maybe_save_result(result)

    def operation_multiply(self):
        self.print_header("MATRIX MULTIPLICATION (A x B)")
        a = self.select_matrix("First matrix name: ")
        if a is None:
            return
        b = self.select_matrix("Second matrix name: ")
        if b is None:
            return
        A, B = self.matrices[a], self.matrices[b]
        if A.shape[1] != B.shape[0]:
            print(f"Error: cannot multiply {A.shape} by {B.shape}. "
                  f"Columns of '{a}' must equal rows of '{b}'.")
            return
        result = A @ B
        print(f"\nResult of '{a}' x '{b}':")
        print(self.format_matrix(result))
        self.maybe_save_result(result)

    def operation_scalar_multiply(self):
        self.print_header("SCALAR MULTIPLICATION (k x A)")
        a = self.select_matrix("Matrix name: ")
        if a is None:
            return
        try:
            k = float(input("Enter the scalar value k: "))
        except ValueError:
            print("Invalid number.")
            return
        result = k * self.matrices[a]
        print(f"\nResult of {k} x '{a}':")
        print(self.format_matrix(result))
        self.maybe_save_result(result)

    def operation_transpose(self):
        self.print_header("TRANSPOSE")
        a = self.select_matrix("Matrix name: ")
        if a is None:
            return
        result = self.matrices[a].T
        print(f"\nTranspose of '{a}':")
        print(self.format_matrix(result))
        self.maybe_save_result(result)

    def operation_determinant(self):
        self.print_header("DETERMINANT")
        a = self.select_matrix("Matrix name: ")
        if a is None:
            return
        A = self.matrices[a]
        if A.shape[0] != A.shape[1]:
            print("Error: Determinant is only defined for square matrices.")
            return
        det = np.linalg.det(A)
        print(f"\nDeterminant of '{a}' = {det:.6g}")

    def operation_inverse(self):
        self.print_header("INVERSE")
        a = self.select_matrix("Matrix name: ")
        if a is None:
            return
        A = self.matrices[a]
        if A.shape[0] != A.shape[1]:
            print("Error: Inverse is only defined for square matrices.")
            return
        try:
            inv = np.linalg.inv(A)
        except np.linalg.LinAlgError:
            print("Error: Matrix is singular (determinant = 0) and cannot be inverted.")
            return
        print(f"\nInverse of '{a}':")
        print(self.format_matrix(inv))
        self.maybe_save_result(inv)

    def operation_rank(self):
        self.print_header("RANK")
        a = self.select_matrix("Matrix name: ")
        if a is None:
            return
        rank = np.linalg.matrix_rank(self.matrices[a])
        print(f"\nRank of '{a}' = {rank}")

    def operation_trace(self):
        self.print_header("TRACE")
        a = self.select_matrix("Matrix name: ")
        if a is None:
            return
        A = self.matrices[a]
        if A.shape[0] != A.shape[1]:
            print("Error: Trace is only defined for square matrices.")
            return
        print(f"\nTrace of '{a}' = {np.trace(A):.6g}")

    def operation_eigen(self):
        self.print_header("EIGENVALUES & EIGENVECTORS")
        a = self.select_matrix("Matrix name: ")
        if a is None:
            return
        A = self.matrices[a]
        if A.shape[0] != A.shape[1]:
            print("Error: Eigen-decomposition requires a square matrix.")
            return
        eigenvalues, eigenvectors = np.linalg.eig(A)
        print(f"\nEigenvalues of '{a}':")
        for i, val in enumerate(eigenvalues, start=1):
            print(f"  λ{i} = {val:.4g}")
        print("\nEigenvectors (as columns):")
        print(self.format_matrix(eigenvectors))

    def operation_solve(self):
        self.print_header("SOLVE LINEAR SYSTEM (A x X = B)")
        a = self.select_matrix("Coefficient matrix A (square): ")
        if a is None:
            return
        b = self.select_matrix("Right-hand side matrix/vector B: ")
        if b is None:
            return
        A, B = self.matrices[a], self.matrices[b]
        if A.shape[0] != A.shape[1]:
            print("Error: A must be a square matrix to solve Ax = B.")
            return
        if A.shape[0] != B.shape[0]:
            print(f"Error: A has {A.shape[0]} rows but B has {B.shape[0]} rows; they must match.")
            return
        try:
            solution = np.linalg.solve(A, B)
        except np.linalg.LinAlgError:
            print("Error: A is singular; the system has no unique solution.")
            return
        print("\nSolution X:")
        print(self.format_matrix(solution))
        self.maybe_save_result(solution)

    
    # File persistence
   
    def save_to_file(self):
        self.print_header("SAVE MATRICES TO FILE")
        if not self.matrices:
            print("No matrices to save.")
            return
        filename = input("Enter filename to save as (e.g. my_matrices.npz): ").strip()
        if not filename.endswith(".npz"):
            filename += ".npz"
        np.savez(filename, **self.matrices)
        print(f"Saved {len(self.matrices)} matrix(es) to '{filename}'.")

    def load_from_file(self):
        self.print_header("LOAD MATRICES FROM FILE")
        filename = input("Enter filename to load (e.g. my_matrices.npz): ").strip()
        if not filename.endswith(".npz"):
            filename += ".npz"
        if not os.path.exists(filename):
            print(f"File '{filename}' not found in the current folder.")
            return
        data = np.load(filename)
        for name in data.files:
            self.matrices[name] = data[name]
        print(f"Loaded matrices: {', '.join(data.files)}")

   
    # Main menu loop

    def run(self):
        self.print_header("WELCOME TO THE MATRIX OPERATIONS TOOL")
        print("Built with Python + NumPy".center(64))

        menu = {
            "1": ("Create / input a new matrix", self.create_matrix),
            "2": ("Display all matrices", self.display_all),
            "3": ("Addition (A + B)", self.operation_add),
            "4": ("Subtraction (A - B)", self.operation_subtract),
            "5": ("Matrix multiplication (A x B)", self.operation_multiply),
            "6": ("Scalar multiplication (k x A)", self.operation_scalar_multiply),
            "7": ("Transpose", self.operation_transpose),
            "8": ("Determinant", self.operation_determinant),
            "9": ("Inverse", self.operation_inverse),
            "10": ("Rank", self.operation_rank),
            "11": ("Trace", self.operation_trace),
            "12": ("Eigenvalues & eigenvectors", self.operation_eigen),
            "13": ("Solve linear system (Ax = B)", self.operation_solve),
            "14": ("Delete a matrix", self.delete_matrix),
            "15": ("Save matrices to file", self.save_to_file),
            "16": ("Load matrices from file", self.load_from_file),
            "0": ("Exit", None),
        }

        while True:
            self.print_header("MAIN MENU")
            for key in sorted(menu.keys(), key=int):
                print(f"  {key:>2}. {menu[key][0]}")
            choice = input("\nEnter your choice: ").strip()

            if choice == "0":
                print("\nThank you for using the Matrix Operations Tool. Goodbye!")
                break
            elif choice in menu:
                try:
                    menu[choice][1]()
                except Exception as e:
                    print(f"\nAn unexpected error occurred: {e}")
                input("\nPress Enter to continue...")
            else:
                print("Invalid choice. Please pick a number from the menu.")


if __name__ == "__main__":
    try:
        app = MatrixOperationsTool()
        app.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)