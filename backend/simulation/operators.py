def calculate_operators(

    machines,

    equipment

):

    minimum = (

        equipment["no_operators_min"]

        or 0

    )

    maximum = (

        equipment["no_operators_max"]

        or minimum

    )

    return {

        "operators_min":

            machines * minimum,

        "operators_max":

            machines * maximum

    }