
import re
import math
from typing import Optional

from processors.base_processor import BaseProcessor, ProcessorContext
from utils.logger import get_logger

logger = get_logger(__name__)

# Unit conversion table 
UNIT_CONVERSIONS = {
    # Length
    "km": ("m", 1000), "kilometer": ("m", 1000), "kilometres": ("m", 1000),
    "mi": ("m", 1609.344), "mile": ("m", 1609.344), "miles": ("m", 1609.344),
    "ft": ("m", 0.3048), "feet": ("m", 0.3048), "foot": ("m", 0.3048),
    "in": ("m", 0.0254), "inch": ("m", 0.0254), "inches": ("m", 0.0254),
    "cm": ("m", 0.01), "centimeter": ("m", 0.01),
    "mm": ("m", 0.001), "millimeter": ("m", 0.001),
    "m": ("m", 1), "meter": ("m", 1), "meters": ("m", 1),
    "yd": ("m", 0.9144), "yard": ("m", 0.9144), "yards": ("m", 0.9144),
    # Weight
    "kg": ("g", 1000), "kilogram": ("g", 1000),
    "lb": ("g", 453.592), "pound": ("g", 453.592), "pounds": ("g", 453.592),
    "oz": ("g", 28.3495), "ounce": ("g", 28.3495), "ounces": ("g", 28.3495),
    "g": ("g", 1), "gram": ("g", 1), "grams": ("g", 1),
    "t": ("g", 1_000_000), "tonne": ("g", 1_000_000),
    # Temperature (special handling)
    "c": ("temp_c", 1), "celsius": ("temp_c", 1),
    "f": ("temp_f", 1), "fahrenheit": ("temp_f", 1),
    "k": ("temp_k", 1), "kelvin": ("temp_k", 1),
    # Speed
    "kmh": ("ms", 1/3.6), "kph": ("ms", 1/3.6),
    "mph": ("ms", 0.44704),
    "ms": ("ms", 1), "m/s": ("ms", 1),
    # Volume
    "l": ("ml", 1000), "liter": ("ml", 1000), "litre": ("ml", 1000),
    "ml": ("ml", 1), "milliliter": ("ml", 1),
    "gal": ("ml", 3785.41), "gallon": ("ml", 3785.41),
    "floz": ("ml", 29.5735), "fl oz": ("ml", 29.5735),
    # Time
    "s": ("s", 1), "sec": ("s", 1), "second": ("s", 1), "seconds": ("s", 1),
    "min": ("s", 60), "minute": ("s", 60), "minutes": ("s", 60),
    "hr": ("s", 3600), "hour": ("s", 3600), "hours": ("s", 3600),
    "day": ("s", 86400), "days": ("s", 86400),
    "week": ("s", 604800), "weeks": ("s", 604800),
    "year": ("s", 31_536_000), "years": ("s", 31_536_000),
}

CONSTANTS = {
    "pi": (math.pi, "Pi is approximately 3.14159265358979"),
    "e": (math.e, "Euler's number e is approximately 2.71828182845905"),
    "phi": (1.6180339887, "The golden ratio phi is approximately 1.6180339887"),
    "speed of light": (299_792_458, "The speed of light is 299,792,458 meters per second"),
    "gravitational constant": (6.674e-11, "G is approximately 6.674 × 10⁻¹¹ N·m²/kg²"),
    "avogadro": (6.022e23, "Avogadro's number is approximately 6.022 × 10²³"),
    "planck": (6.626e-34, "Planck's constant is approximately 6.626 × 10⁻³⁴ J·s"),
}


class MathProcessor(BaseProcessor):
    name = "math"
    description = "Perform calculations, unit conversions, and algebra"
    triggers = [
        r"\b(calculate|compute|calc)\b",
        r"\bwhat(?:'s| is) (?:\d|the result of|the answer to)\b",
        r"\bhow much is\b",
        r"\b\d+\s*[\+\-\*\/\^]\s*\d+\b",
        r"\bsquare root of\b",
        r"\b(sin|cos|tan|log|sqrt|factorial)\b",
        r"\bconvert\b.*\bto\b",
        r"\bhow many\b.*\bin\b",
        r"\bwhat is\s+\d",
        r"\b(pi|euler|golden ratio|speed of light|avogadro|planck)\b",
        r"\bpercent(age)?\b.*\bof\b",
        r"\b\d+\s*%\s*of\b",
        r"\bsolve\b",
        r"\bequation\b",
    ]

    def __init__(self, config: dict, llm_client=None):
        super().__init__(config)
        self.llm = llm_client

    def process(self, text: str, context: ProcessorContext) -> str:
        # Update LLM ref from context
        if not self.llm and context.llm:
            self.llm = context.llm

        text_lower = text.lower().strip()

        # Constants ----------------------------------------------------------------------------------
        for const_name, (value, description) in CONSTANTS.items():
            if const_name in text_lower:
                return description + f" ({value:.6g})."

        # Unit conversion ----------------------------------------------------------------------------
        conversion_result = self._try_unit_conversion(text_lower)
        if conversion_result:
            return conversion_result

        #  Percentage ------------------------------------------------------------------------------
        pct_result = self._try_percentage(text_lower)
        if pct_result:
            return pct_result

        # Direct arithmetic evaluation -------------------------------------------------------------
        calc_result = self._try_evaluate(text_lower)
        if calc_result is not None:
            return calc_result

        # Sympy algebra ----------------------------------------------------------------------------
        sympy_result = self._try_sympy(text_lower)
        if sympy_result:
            return sympy_result

        # LLM fallback for complex problems --------------------------------------------------------
        if self.llm:
            prompt = (
                f"Solve this math problem step by step, then give the final answer clearly. "
                f"Be concise — speak the answer for audio: {text}"
            )
            result = self.llm.generate_simple(prompt)
            return result or "I couldn't solve that math problem."

        return "I couldn't compute that. Try rephrasing the math problem."

    def _try_evaluate(self, text: str) -> Optional[str]:
        """Safe arithmetic evaluation."""
        # Extract math expression
        # Replace words with operators
        expr = text
        replacements = {
            r"\bplus\b": "+", r"\bminus\b": "-", r"\btimes\b": "*",
            r"\bdivided by\b": "/", r"\bover\b": "/",
            r"\bto the power of\b": "**", r"\bsquared\b": "**2",
            r"\bcubed\b": "**3", r"\bsquare root of\b": "math.sqrt",
            r"\bsqrt\b": "math.sqrt",
            r"\bsin\b": "math.sin", r"\bcos\b": "math.cos",
            r"\btan\b": "math.tan",
            r"\blog\b": "math.log10", r"\bln\b": "math.log",
            r"\bfactorial of\b": "math.factorial",
            r"\bpi\b": "math.pi", r"\be\b": "math.e",
            r"what(?:'s| is) ": "", r"calculate ": "",
            r"compute ": "", r"the result of ": "",
        }
        for pattern, replacement in replacements.items():
            expr = re.sub(pattern, replacement, expr, flags=re.IGNORECASE)

        # Extract the expression (only math-safe characters)
        match = re.search(
            r"[\d\+\-\*\/\(\)\.\^\s]+(?:math\.\w+\([^)]*\))?[\d\+\-\*\/\(\)\.\s]*",
            expr,
        )
        if not match:
            return None

        raw_expr = match.group(0).strip()
        if not raw_expr or re.match(r"^\s*\d+\s*$", raw_expr):
            # Single number, not interesting
            return None

        try:
            # Safe eval: only math module allowed
            result = eval(raw_expr, {"__builtins__": {}, "math": math})

            if isinstance(result, float):
                if result == int(result):
                    formatted = f"{int(result):,}"
                else:
                    formatted = f"{result:.6g}"
            else:
                formatted = f"{result:,}"

            return f"The answer is {formatted}."
        except Exception:
            return None

    def _try_unit_conversion(self, text: str) -> Optional[str]:
        """Parse and execute unit conversion."""
        # Pattern: "convert X unit to unit" or "X unit in unit"
        patterns = [
            r"convert\s+([\d.]+)\s+(\w+)\s+to\s+(\w+)",
            r"([\d.]+)\s+(\w+)\s+(?:in|to|into)\s+(\w+)",
            r"how many\s+(\w+)\s+(?:in|are in)\s+([\d.]+)\s+(\w+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    if pattern.startswith("how many"):
                        to_unit, amount_str, from_unit = groups
                    else:
                        amount_str, from_unit, to_unit = groups
                    try:
                        amount = float(amount_str)
                        result = self._convert_units(amount, from_unit.lower(), to_unit.lower())
                        if result is not None:
                            return result
                    except ValueError:
                        pass
        return None

    def _convert_units(self, amount: float, from_unit: str, to_unit: str) -> Optional[str]:
        """Perform unit conversion."""
        # Temperature special case
        temp_units = {"c": "celsius", "f": "fahrenheit", "k": "kelvin",
                      "celsius": "celsius", "fahrenheit": "fahrenheit", "kelvin": "kelvin"}

        fu = from_unit.rstrip("s")  # Handle plural
        tu = to_unit.rstrip("s")

        if fu in temp_units or from_unit in temp_units:
            return self._convert_temperature(amount, from_unit, to_unit)

        # General conversion via SI
        from_info = UNIT_CONVERSIONS.get(from_unit) or UNIT_CONVERSIONS.get(fu)
        to_info = UNIT_CONVERSIONS.get(to_unit) or UNIT_CONVERSIONS.get(tu)

        if not from_info or not to_info:
            return None

        from_base, from_factor = from_info
        to_base, to_factor = to_info

        if from_base != to_base:
            return None  # Incompatible units

        result = amount * from_factor / to_factor

        if result == int(result):
            result_str = f"{int(result):,}"
        else:
            result_str = f"{result:.4g}"

        return f"{amount:g} {from_unit} is {result_str} {to_unit}."

     def _convert_temperature(self, amount: float, from_unit: str, to_unit: str) -> Optional[str]:
        #Convert temperature between C, F, K.
        fu = from_unit[0].lower()
        tu = to_unit[0].lower()

        # Convert to Celsius first
        if fu == "f":
            celsius = (amount - 32) * 5 / 9
        elif fu == "k":
            celsius = amount - 273.15
        else:
            celsius = amount

        # Convert from Celsius to target
        if tu == "f":
            result = celsius * 9 / 5 + 32
            unit_name = "Fahrenheit"
        elif tu == "k":
            result = celsius + 273.15
            unit_name = "Kelvin"
        else:
            result = celsius
            unit_name = "Celsius"

        return f"{amount}° {from_unit.capitalize()} is {result:.1f}° {unit_name}."
    def _try_percentage(self, text: str) -> Optional[str]:
        """Handle percentage calculations."""
        # "X% of Y"
        match = re.search(r"([\d.]+)\s*%\s*of\s*([\d,]+)", text)
        if match:
            pct = float(match.group(1))
            total = float(match.group(2).replace(",", ""))
            result = pct / 100 * total
            return f"{pct}% of {total:g} is {result:.4g}."

        # "what percent is X of Y"
        match = re.search(r"what percent(?:age)? is ([\d.]+) of ([\d.]+)", text)
        if match:
            part = float(match.group(1))
            whole = float(match.group(2))
            if whole == 0:
                return "Can't divide by zero."
            pct = (part / whole) * 100
            return f"{part} is {pct:.2f}% of {whole}."

        return None

    def _try_sympy(self, text: str) -> Optional[str]:
        """Use sympy for algebra and symbolic math."""
        try:
            import sympy as sp

            # Basic solve pattern: "solve X squared + 5X + 6 = 0"
            match = re.search(r"solve\s+(.+?)(?:\s*=\s*0)?$", text)
            if match:
                expr_str = match.group(1)
                expr_str = re.sub(r"(\d+)?x", lambda m: f"{m.group(1) or ''}*x", expr_str)
                expr_str = re.sub(r"squared", "**2", expr_str)
                expr_str = re.sub(r"cubed", "**3", expr_str)

                x = sp.Symbol("x")
                try:
                    expr = sp.sympify(expr_str)
                    solutions = sp.solve(expr, x)
                    if solutions:
                        sol_strs = [str(sp.nsimplify(s, rational=False)) for s in solutions]
                        return f"The solutions are: {', '.join(sol_strs)}."
                except Exception:
                    pass
        except ImportError:
            pass
        return None
