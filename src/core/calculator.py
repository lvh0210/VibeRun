import math
import re

SAFE_MATH_NAMES = {
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'log': math.log,
    'log10': math.log10,
    'log2': math.log2,
    'exp': math.exp,
    'abs': abs,
    'round': round,
    'floor': math.floor,
    'ceil': math.ceil,
    'pow': pow,
    'pi': math.pi,
    'e': math.e
}

class Calculator:
    """Evaluates safe arithmetic expressions quickly without overhead."""

    @staticmethod
    def calculate(query: str):
        query = query.strip()
        if not query:
            return None

        # Check for "=" prefix or if query contains math operators
        has_equal_prefix = query.startswith("=")
        raw_expr = query[1:].strip() if has_equal_prefix else query

        # Handle 'X% of Y' pattern
        pct_match = re.match(r"^([\d.]+)\s*%\s*(?:of)?\s*([\d.]+)$", raw_expr, re.IGNORECASE)
        if pct_match:
            try:
                p = float(pct_match.group(1))
                val = float(pct_match.group(2))
                res = (p / 100.0) * val
                return Calculator._format_result(raw_expr, res)
            except Exception:
                return None

        # Replace ^ with ** for exponents
        expr = raw_expr.replace("^", "**")

        # Must have at least some digit or math function to be considered math
        if not re.search(r"\d", expr) and not any(fn in expr for fn in ["pi", "e"]):
            return None

        # If not prefixed with =, check if expression strictly looks like math
        if not has_equal_prefix:
            # Must contain at least one math operator or known math function
            if not re.search(r"[\+\-\*\/\%\(\)]", expr) and not any(fn in expr for fn in SAFE_MATH_NAMES):
                return None
            # Disallow characters not part of math syntax
            if re.search(r"[a-zA-Z_]", expr):
                # Only allowed words are in SAFE_MATH_NAMES
                words = re.findall(r"[a-zA-Z_]+", expr)
                if not all(w in SAFE_MATH_NAMES for w in words):
                    return None

        try:
            # Compile into code object with eval mode
            code = compile(expr, "<string>", "eval")
            # Ensure no code attributes or __ builtins
            for name in code.co_names:
                if name not in SAFE_MATH_NAMES:
                    return None

            result = eval(code, {"__builtins__": {}}, SAFE_MATH_NAMES)
            if isinstance(result, (int, float, complex)):
                return Calculator._format_result(raw_expr, result)
        except Exception:
            return None

        return None

    @staticmethod
    def _format_result(expr: str, val):
        if isinstance(val, float):
            if val.is_integer():
                formatted = str(int(val))
            else:
                formatted = f"{val:.6g}"
        else:
            formatted = str(val)

        return {
            "title": f"= {formatted}",
            "subtitle": f"Calculation: {expr} (Press Enter to copy result)",
            "type": "calc",
            "target": formatted,
            "badge": "CALC",
            "score": 1000
        }
